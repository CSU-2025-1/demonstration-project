import os


class Settings:
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@haproxy:5432/postgres"
    )


settings = Settings()
