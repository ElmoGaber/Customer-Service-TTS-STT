# orchestrator/storage_s3.py
from __future__ import annotations
import pathlib

try:
    import boto3
except Exception:
    boto3 = None  # type: ignore

from orchestrator.config import load_env

SETTINGS = load_env()

# Always anchor to project root (where server.py lives)
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
SESS_DIR = BASE_DIR / "sessions"


def ensure_sessions_dir():
    """Create the sessions/ folder if it does not exist."""
    SESS_DIR.mkdir(parents=True, exist_ok=True)


def save_html_report(session_id: str, html: str) -> str:
    """
    Save an HTML troubleshooting report.
    - If USE_S3=0: save locally in <project>/sessions/<id>.html
      and return a relative web path (/sessions/<id>.html)
      that FastAPI can serve when mounted.
    - If USE_S3=1: upload to S3 and return a presigned URL.
    """
    ensure_sessions_dir()

    if not SETTINGS.USE_S3:
        path = SESS_DIR / f"{session_id}.html"
        path.write_text(html, encoding="utf-8")
        # This assumes server.py mounts app.mount("/sessions", SESS_DIR, ...)
        return f"/sessions/{session_id}.html"

    if boto3 is None:
        raise RuntimeError("boto3 not installed or unavailable")

    s3 = boto3.client(
        "s3",
        endpoint_url=SETTINGS.S3_ENDPOINT_URL or None,
        region_name=SETTINGS.S3_REGION or None,
        aws_access_key_id=SETTINGS.S3_ACCESS_KEY_ID or None,
        aws_secret_access_key=SETTINGS.S3_SECRET_ACCESS_KEY or None,
    )

    key_prefix = (SETTINGS.S3_PREFIX or "").rstrip("/")
    key = f"{key_prefix}/{session_id}.html" if key_prefix else f"{session_id}.html"

    s3.put_object(
        Bucket=SETTINGS.S3_BUCKET,
        Key=key,
        Body=html.encode("utf-8"),
        ContentType="text/html",
    )

    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": SETTINGS.S3_BUCKET, "Key": key},
        ExpiresIn=SETTINGS.S3_PRESIGN_EXPIRES,
    )
    return url
