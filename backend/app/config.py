from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    k8s_namespace: str = "autosre-demo"
    safe_mode: bool = True
    ollama_enabled: bool = False
    ollama_model: str = ""
    ollama_url: str = "http://localhost:11434"
    prometheus_url: str = ""
    loki_url: str = ""
    chroma_path: str = "./data/chroma"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
