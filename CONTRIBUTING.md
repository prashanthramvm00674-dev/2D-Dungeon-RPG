# Contributing and development workflow

This project uses feature branches, pull requests, and automated regression checks. Keep main releasable: do not develop directly on it.

## Branch naming

Use feature branches for gameplay or UI work, fix branches for bug fixes, automation branches for tooling, and test branches for test-only changes.

Open a pull request targeting main. Describe the scope, risks, test results, and any manual gameplay checks.

## Local setup

From the repository root in PowerShell:

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

Run the game:

    python src\main.py

## Run checks

Compile the source and tests:

    python -m compileall -q src tests

Run every regression script discovered under tests/test_*.py:

    python tests\run_regression.py

Run one or more specific tests:

    python tests\run_regression.py --test test_boss_encounter.py
    python tests\run_regression.py --test test_boss_encounter.py --test test_persistence.py

The runner sets SDL's dummy video and audio drivers for headless test execution. It writes per-test logs, a Markdown summary, and JSON results to artifacts/test-reports/. That folder is generated output and is excluded from Git.

## Continuous integration

GitHub Actions runs the regression suite on Python 3.13 on Ubuntu and Windows for pushes to supported development branches and for pull requests targeting main. The test runner discovers test_*.py scripts automatically, so newly added tests join CI without maintaining a second list.

The Windows packaging workflow also builds a standalone ZIP on pull requests targeting main. The main regression workflow independently runs the full test suite on Ubuntu and Windows. Starting the packaging workflow manually, or pushing a version tag such as v1.1.0, runs the full regression suite before building. Version tags publish the tested ZIP as a GitHub Release asset.

## Change safety

- Keep changes focused and avoid unrelated refactors.
- Add or update regression tests for bug fixes and new behaviour.
- Preserve existing save data, settings, and controls unless a change explicitly requires otherwise.
- Never treat a headless graphics test as a replacement for checking the game on a real Windows desktop.
- Review the pull request diff and successful CI checks before merging.
