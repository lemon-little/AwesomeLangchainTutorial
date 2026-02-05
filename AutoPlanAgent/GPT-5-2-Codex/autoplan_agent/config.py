import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


@dataclass
class Settings:
    openai_api_key: str
    openai_base_url: str
    openai_model: str
    tavily_api_key: str
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_db: str
    state_dir: str
    output_dir: str
    tool_modules: list[str]
    log_file: str

    @staticmethod
    def load() -> "Settings":
        if load_dotenv:
            load_dotenv()
            load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        return Settings(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_base_url=os.getenv("OPENAI_BASE_URL", ""),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
            mysql_host=os.getenv("MYSQL_HOST", "localhost"),
            mysql_port=int(os.getenv("MYSQL_PORT", "3306")),
            mysql_user=os.getenv("MYSQL_USER", "root"),
            mysql_password=os.getenv("MYSQL_PASSWORD", ""),
            mysql_db=os.getenv("MYSQL_DB", "test"),
            state_dir=os.getenv("STATE_DIR", "./state"),
            output_dir=os.getenv("OUTPUT_DIR", "./outputs"),
            tool_modules=[m for m in os.getenv("TOOL_MODULES", "").split(",") if m],
            log_file=os.getenv("LOG_FILE", "./outputs/agent.log"),
        )
