import os
from pathlib import Path


ENV_FILE = Path(__file__).resolve().parent / ".env"


def _load_env_file() -> None:
    """Load environment variables from app/config/.env."""
    if not ENV_FILE.exists():
        return

    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(dotenv_path=ENV_FILE, override=False)
        return
    except Exception:
        pass

    # Fallback parser when python-dotenv is unavailable.
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file()


class ClickHouseSettings:
    def __init__(self) -> None:
        self.HOST: str = os.getenv("CLICKHOUSE_HOST", "172.23.216.106")
        self.PORT: int = int(os.getenv("CLICKHOUSE_PORT", "8123"))
        self.USER: str = os.getenv("CLICKHOUSE_USER", "default")
        self.PASSWORD: str = os.getenv("CLICKHOUSE_PASSWORD", "clickhouse")
        self.DATABASE: str = os.getenv("CLICKHOUSE_DATABASE", "hawkeye_test")


class LLMSettings:
    def __init__(self) -> None:
        self.API_BASE: str = os.getenv("LLM_API_BASE", "http://172.23.216.104:6006/v1")
        self.API_KEY: str = os.getenv("LLM_API_KEY", "EMPTY")
        # self.MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "Qwen3-14B")
        self.MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "Qwen3.6-35B-A3B")


class MilvusSettings:
    def __init__(self) -> None:
        self.HOST: str = os.getenv("MILVUS_HOST", "172.23.216.104")
        self.PORT: str = os.getenv("MILVUS_PORT", "19530")
        self.COLLECTION_NAME: str = os.getenv("MILVUS_COLLECTION_NAME", "ty_content")
        self.EMBEDDING_API_URL: str = os.getenv("EMBEDDING_API_URL", "http://172.23.216.104:5005/v1/embeddings")
        self.DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "4096"))

class RerankSettings:
    def __init__(self) -> None:
        self.MODEL_PATH: str = os.getenv("RERANK_MODEL_PATH", "/data/czr/Ty_front_backend/models/bge-reranker-v2-m3")



ch_settings = ClickHouseSettings()
llm_settings = LLMSettings()
milvus_settings = MilvusSettings()
rerank_settings = RerankSettings()

