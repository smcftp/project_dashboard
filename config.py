from dash import Dash

from pydantic_settings import BaseSettings

############################################################

# Переменные окружения

class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = 'D:\Programming\Python\ENECA\Dashboard_OCK\test_dashboard_project — копия\.env'

set = Settings()

############################################################

# Инициализация приложения Dash
app = Dash(__name__, suppress_callback_exceptions=False)