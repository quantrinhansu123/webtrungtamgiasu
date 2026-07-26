import sys
from pathlib import Path


# Expose the Flask CMS application to the Vercel Python runtime.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "admin"))

try:
    from server import app  # noqa: E402
except Exception as startup_error:  # pragma: no cover - Vercel bootstrap guard
    from flask import Flask, jsonify

    app = Flask(__name__)

    def startup_error_code(error: Exception) -> str:
        message = str(error)
        if message.startswith("Production CMS requires "):
            return "MISSING_SESSION_SECRET"
        if isinstance(error, ModuleNotFoundError):
            return f"MISSING_DEPENDENCY:{error.name or 'unknown'}"
        return f"STARTUP_ERROR:{type(error).__name__}"

    _STARTUP_ERROR_CODE = startup_error_code(startup_error)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def unavailable(path):
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "CMS chưa khởi động được",
                    "code": _STARTUP_ERROR_CODE,
                }
            ),
            503,
        )
