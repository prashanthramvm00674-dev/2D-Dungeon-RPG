"""Atomic JSON save slots and persistent user settings.

Runtime data is kept outside the source tree in the ignored saves folder.
Writes use a temporary sibling file and replace the target only after JSON has
been fully flushed, preventing partial writes from destroying a prior save.
"""

import json
import os
import tempfile
from pathlib import Path


SAVE_SCHEMA_VERSION = 1
SETTINGS_SCHEMA_VERSION = 1

DEFAULT_SETTINGS = {
    "start_fullscreen": False,
    "lighting_enabled": True,
    "post_processing_enabled": True,
    "autosave_on_quit": True,
}


def _default_data_directory():
    """Resolve the repository root from this module, not the process cwd."""
    return Path(__file__).resolve().parents[2] / "saves"


def _atomic_json_write(path, payload):
    """Write JSON atomically; return (success, error_message)."""
    path = Path(path)
    temporary_path = None

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=str(path.parent),
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())

        os.replace(temporary_path, path)
        return True, ""
    except (OSError, TypeError, ValueError) as exc:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        return False, str(exc)


class SaveManager:
    """Read and write the single manual/auto-save slot."""

    def __init__(self, path=None):
        self.path = Path(path) if path is not None else (
            _default_data_directory() / "save_slot_1.json"
        )
        self.last_error = ""

    def exists(self):
        return self.path.is_file()

    def save(self, payload):
        if (
            not isinstance(payload, dict)
            or payload.get("schema_version") != SAVE_SCHEMA_VERSION
            or not isinstance(payload.get("game"), dict)
        ):
            self.last_error = "The save payload has an unsupported structure."
            return False

        success, error = _atomic_json_write(self.path, payload)
        self.last_error = error
        return success

    def load(self):
        if not self.path.is_file():
            self.last_error = "No saved game was found."
            return None

        try:
            with self.path.open("r", encoding="utf-8") as stream:
                payload = json.load(stream)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            self.last_error = f"The save file could not be read: {exc}"
            return None

        if (
            not isinstance(payload, dict)
            or payload.get("schema_version") != SAVE_SCHEMA_VERSION
            or not isinstance(payload.get("game"), dict)
        ):
            self.last_error = "The save file is invalid or from an unsupported version."
            return None

        self.last_error = ""
        return payload


class SettingsManager:
    """Load, validate, and persist the small set of supported game options."""

    def __init__(self, path=None):
        self.path = Path(path) if path is not None else (
            _default_data_directory() / "settings.json"
        )
        self.values = DEFAULT_SETTINGS.copy()
        self.last_error = ""

    def load(self):
        if not self.path.is_file():
            self.values = DEFAULT_SETTINGS.copy()
            self.last_error = ""
            return self.values.copy()

        try:
            with self.path.open("r", encoding="utf-8") as stream:
                payload = json.load(stream)
            if (
                not isinstance(payload, dict)
                or payload.get("schema_version") != SETTINGS_SCHEMA_VERSION
                or not isinstance(payload.get("settings"), dict)
            ):
                raise ValueError("The settings file has an unsupported structure.")

            raw = payload["settings"]
            values = DEFAULT_SETTINGS.copy()
            for key, default in DEFAULT_SETTINGS.items():
                value = raw.get(key, default)
                if type(value) is not bool:
                    raise ValueError(f"Setting '{key}' must be true or false.")
                values[key] = value

            self.values = values
            self.last_error = ""
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            # A broken preferences file must never prevent the game from starting.
            self.values = DEFAULT_SETTINGS.copy()
            self.last_error = str(exc)

        return self.values.copy()

    def save(self):
        payload = {
            "schema_version": SETTINGS_SCHEMA_VERSION,
            "settings": self.values.copy(),
        }
        success, error = _atomic_json_write(self.path, payload)
        self.last_error = error
        return success

    def set(self, key, value):
        if key not in DEFAULT_SETTINGS:
            raise KeyError(f"Unknown setting: {key}")
        if type(value) is not bool:
            raise ValueError(f"Setting '{key}' must be true or false.")

        previous = self.values[key]
        self.values[key] = value
        if self.save():
            return True

        self.values[key] = previous
        return False

    def toggle(self, key):
        if key not in DEFAULT_SETTINGS:
            raise KeyError(f"Unknown setting: {key}")
        return self.set(key, not self.values[key])
