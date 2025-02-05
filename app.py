from dash import Dash
from layouts.main_layout import create_main_layout
from callbacks import graph_callbacks

from config import app

# Инициализация приложения
app.layout = create_main_layout()

# Подключение обратных вызовов
graph_callbacks.register_graph_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)