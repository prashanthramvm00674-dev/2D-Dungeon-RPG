"""Run every test_*.py script and produce portable CI reports.

Usage:
    python tests/run_regression.py
    python tests/run_regression.py --timeout 300
    python tests/run_regression.py --test test_boss_encounter.py
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = ROOT / "tests"
REPORT_DIR = ROOT / "artifacts" / "test-reports"


def _decode(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _write_report(results: list[dict[str, Any]], started_at: str, elapsed: float) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    passed = sum(item["status"] == "passed" for item in results)
    failed = len(results) - passed
    payload = {
        "started_at_utc": started_at,
        "duration_seconds": round(elapsed, 3),
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "results": results,
    }
    (REPORT_DIR / "test-results.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    lines = [
        "# Dungeon RPG regression report",
        "",
        f"- Started (UTC): {started_at}",
        f"- Duration: {elapsed:.2f} seconds",
        f"- Total: {len(results)}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
        "",
        "| Test | Result | Duration (s) |",
        "|---|---:|---:|",
    ]
    for item in results:
        status = "PASS" if item["status"] == "passed" else "FAIL"
        lines.append(
            f"| {item['test']} | **{status}** | {item['duration_seconds']:.2f} |"
        )
    failures = [item for item in results if item["status"] != "passed"]
    lines.extend(["", "## Failure details", ""])
    if failures:
        for item in failures:
            lines.extend([
                f"### {item['test']}",
                "",
                f"- Status: {item['status']}",
                f"- Exit code: {item['returncode']}",
                f"- Log: {item['log']}",
                "",
            ])
    else:
        lines.append("All discovered regression tests passed.")

    report = "\n".join(lines) + "\n"
    (REPORT_DIR / "test-report.md").write_text(report, encoding="utf-8")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as summary_file:
            summary_file.write(report)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout", type=int, default=240,
        help="Maximum seconds allowed for each test script (default: 240).",
    )
    parser.add_argument(
        "--test", action="append", dest="selected_tests",
        help="Run only this test filename. Can be provided more than once.",
    )
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero.")

    test_files = sorted(TESTS_DIR.glob("test_*.py"))
    if args.selected_tests:
        selected = set(args.selected_tests)
        test_files = [path for path in test_files if path.name in selected]
        missing = selected - {path.name for path in test_files}
        if missing:
            print(f"Unknown test file(s): {', '.join(sorted(missing))}", file=sys.stderr)
            return 2
    if not test_files:
        print("No test_*.py scripts were found.", file=sys.stderr)
        return 2

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc).isoformat()
    suite_started = time.monotonic()
    environment = os.environ.copy()
    environment.update({
        "SDL_VIDEODRIVER": "dummy",
        "SDL_AUDIODRIVER": "dummy",
        "PYGAME_HIDE_SUPPORT_PROMPT": "1",
        "PYTHONUNBUFFERED": "1",
    })

    results: list[dict[str, Any]] = []
    print(f"Discovered {len(test_files)} regression test(s).")
    for index, test_path in enumerate(test_files, start=1):
        relative_path = test_path.relative_to(ROOT).as_posix()
        print(f"[{index}/{len(test_files)}] RUN  {test_path.name}")
        test_started = time.monotonic()
        status = "failed"
        returncode: int | None = None
        stdout = ""
        stderr = ""

        try:
            completed = subprocess.run(
                [sys.executable, str(test_path)],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=args.timeout,
                check=False,
            )
            stdout = completed.stdout
            stderr = completed.stderr
            returncode = completed.returncode
            status = "passed" if returncode == 0 else "failed"
        except subprocess.TimeoutExpired as error:
            stdout = _decode(error.stdout)
            stderr = _decode(error.stderr) + f"\nTimed out after {args.timeout} seconds.\n"
            status = "timeout"
        except OSError as error:
            stderr = f"Could not execute test: {error}\n"
            status = "failed"

        duration = time.monotonic() - test_started
        log_path = REPORT_DIR / f"{test_path.stem}.log"
        log_path.write_text(
            f"Test: {relative_path}\nStatus: {status}\n"
            f"Return code: {returncode}\nDuration: {duration:.3f}s\n\n"
            f"===== STDOUT =====\n{stdout}\n===== STDERR =====\n{stderr}\n",
            encoding="utf-8",
        )
        result = {
            "test": test_path.name,
            "status": status,
            "returncode": returncode,
            "duration_seconds": round(duration, 3),
            "log": log_path.relative_to(ROOT).as_posix(),
        }
        results.append(result)

        if status == "passed":
            print(f"[{index}/{len(test_files)}] PASS {test_path.name} ({duration:.2f}s)")
        else:
            print(f"[{index}/{len(test_files)}] FAIL {test_path.name} ({status})")
            detail = (stdout + "\n" + stderr).strip()
            if detail:
                print(detail[-12000:])

    elapsed = time.monotonic() - suite_started
    _write_report(results, started_at, elapsed)
    passed = sum(item["status"] == "passed" for item in results)
    failed = len(results) - passed
    print(f"\nRegression summary: {passed}/{len(results)} passed; {failed} failed.")
    print(f"Reports written to: {REPORT_DIR.relative_to(ROOT)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
