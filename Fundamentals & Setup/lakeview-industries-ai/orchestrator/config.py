from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str
    CHAT_MODEL: str
    STT_MODEL: str
    CHECKPOINT_DB: str
    REQUIRE_CONFIRM_BEFORE_NOTIFY: bool
    USE_S3: bool
    S3_ENDPOINT_URL: str
    S3_REGION: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_BUCKET: str
    S3_PREFIX: str
    S3_PRESIGN_EXPIRES: int
    FROM_EMAIL: str
    SUPERVISOR_EMAIL: str
    ORG_NAME: str

def load_env() -> Settings:
    load_dotenv()
    def b(name, default="0"):
        try:
            return bool(int(os.getenv(name, default)))
        except Exception:
            return os.getenv(name, default) in ("true","True","YES","yes")
    return Settings(
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY",""),
        OPENAI_BASE_URL=os.getenv("OPENAI_BASE_URL",""),
        CHAT_MODEL=os.getenv("CHAT_MODEL","gpt-4o-mini"),
        STT_MODEL=os.getenv("STT_MODEL","gpt-4o-mini-transcribe"),
        CHECKPOINT_DB=os.getenv("CHECKPOINT_DB","orchestrator_checkpoints.sqlite"),
        REQUIRE_CONFIRM_BEFORE_NOTIFY=b("REQUIRE_CONFIRM_BEFORE_NOTIFY","1"),
        USE_S3=b("USE_S3","0"),
        S3_ENDPOINT_URL=os.getenv("S3_ENDPOINT_URL","https://s3.us-east-2.amazonaws.com"),
        S3_REGION=os.getenv("S3_REGION","us-east-2"),
        S3_ACCESS_KEY_ID=os.getenv("S3_ACCESS_KEY_ID",""),
        S3_SECRET_ACCESS_KEY=os.getenv("S3_SECRET_ACCESS_KEY",""),
        S3_BUCKET=os.getenv("S3_BUCKET","ironpath-reports"),
        S3_PREFIX=os.getenv("S3_PREFIX","reports"),
        S3_PRESIGN_EXPIRES=int(os.getenv("S3_PRESIGN_EXPIRES","86400")),
        FROM_EMAIL=os.getenv("FROM_EMAIL","alerts@example.com"),
        SUPERVISOR_EMAIL=os.getenv("SUPERVISOR_EMAIL","ops@example.com"),
        ORG_NAME=os.getenv("ORG_NAME","IronPath AI"),
    )
