import sys
from pathlib import Path


# Expose the Flask CMS application to the Vercel Python runtime.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "admin"))

from server import app  # noqa: E402

