from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str
    saramin_api_key: str = ""
    chroma_path: str = "./data/chroma"
    database_url: str = "sqlite:///./data/jobs.db"
    top_k: int = 5

    model_config = {"env_file": ".env"}


settings = Settings()
