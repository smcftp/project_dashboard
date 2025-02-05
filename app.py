import os
from dash import Dash
from layouts.main_layout import create_main_layout
from callbacks import graph_callbacks

# Импорт приложения
from config import app

# Инициализация приложения
app.layout = create_main_layout()

# Подключение обратных вызовов
graph_callbacks.register_graph_callbacks(app)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # Используем порт от Railway
    app.run_server(host="0.0.0.0", port=port, debug=True)
