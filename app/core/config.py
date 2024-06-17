from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_user: str
    db_pass: str
    db_port: str

# settings = Settings()
