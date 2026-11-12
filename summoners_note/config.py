import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    RIOT_API_KEY = os.getenv("RIOT_API_KEY")
    RIOT_REGIONAL_ROUTE = os.getenv("RIOT_REGIONAL_ROUTE", "asia")
    RIOT_API_TIMEOUT = (3.05, 10.0)
