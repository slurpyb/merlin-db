from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mdb_path: str = "../data/20230514/GeniSys.mdb"


@lru_cache
def get_settings() -> Settings:
    return Settings()
