from pydantic_settings import BaseSettings, SettingsConfigDict

class Config:
    API_URL = "http://api"
    API_PORT = 8000


config = Config()