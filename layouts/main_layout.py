from dash import dcc, html, dash_table, callback_context
from dash_daq import ToggleSwitch

import database.db as database

from services.project_service import get_project_list

def create_main_layout():
    
    db = next(database.get_db())

    layout = html.Div(
        # Main container style
        style={
            "height": "100vh",
            "display": "flex",
            "flexDirection": "row",
            "alignItems": "flex-start",
            "justifyContent": "flex-start",
            "background": "linear-gradient(135deg, #f5f7fa, #c3cfe2)",
            "padding": "20px",
            "overflow": "hidden",
            "maxHeight": "100vh",
            "gap": "1%",
        },
        children=[
            # State for table visibility
            dcc.Store(
                id="store-show-table",  # State store for table visibility
                data={"show_table": True}
            ),

            # Left Dashboard Section
            html.Div(
                id="left-dashboard-container",  # Left dashboard section
                style={
                    "position": "relative",
                    "width": "60%",
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "flex-start",
                    "background": "#ffffff",
                    "padding": "20px",
                    "borderRadius": "15px",
                    "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                    "maxHeight": "95vh",
                },
                children=[
                    html.Div(
                        id="left-background-frame",  # Background frame for left section
                        style={
                            "position": "absolute",
                            "top": "-15px",
                            "left": "-15px",
                            "right": "-15px",
                            "bottom": "-15px",
                            "zIndex": "-1",
                            "borderRadius": "20px",
                            "background": "rgba(64, 186, 129, 0.05)",
                            "boxShadow": "0 8px 20px rgba(0, 0, 0, 0.2)",
                        },
                    ),
                    html.H1(
                        id="dashboard-title",  # Title of the dashboard
                        children="Интерактивная аналитика",
                        style={
                            "textAlign": "left",
                            "color": "#333",
                            "fontSize": "2rem",
                            "fontWeight": "bold",
                            "marginBottom": "20px",
                            "textShadow": "1px 1px 3px rgba(0, 0, 0, 0.1)",
                        },
                    ),

                    # Dropdown and Interval Selection Container
                    html.Div(
                        id="dropdown-and-interval-container",  # Container for dropdown and interval buttons
                        style={
                            "display": "flex",
                            "flexDirection": "row",
                            "justifyContent": "space-between",
                            "alignItems": "center",
                            "width": "100%",
                            "background": "#f9f9f9",
                            "padding": "15px 20px",
                            "borderRadius": "10px",
                            "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.05)",
                            "boxSizing": "border-box",
                            "gap": "3%",
                        },
                        children=[
                            
                            dcc.Dropdown(
                                id="project-dropdown",
                                options=get_project_list(db=db),
                                placeholder="Выберите проект",
                                className="custom-dropdown",
                                style={
                                    "width": "100%",
                                    "padding": "0.1%",
                                    "border": "1px solid #ddd",
                                    "borderRadius": "8px",
                                    "background": "#f9f9f9",
                                    "fontSize": "1rem",
                                    "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                                    "lineHeight": "1.5",
                                },
                            ),
                            
                            dcc.Dropdown(
                                id="title-dropdown",
                                options=[],
                                placeholder="Выберите титул",
                                className="custom-dropdown-title",
                                style={
                                    "width": "100%",
                                    "padding": "0.1%",
                                    "border": "1px solid #ddd",
                                    "borderRadius": "8px",
                                    "background": "#f9f9f9",
                                    "fontSize": "1rem",
                                    "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                                    "lineHeight": "1.5",
                                },
                            ),
                            
                            # dcc.Dropdown(
                            #     id="project-dropdown",  # Dropdown for project selection
                            #     options=[],
                            #     placeholder="Выберите проект",
                            #     style={
                            #         "width": "100%",
                            #         "padding": "0.1%",
                            #         "border": "1px solid #ddd",
                            #         "borderRadius": "8px",
                            #         "background": "#f9f9f9",
                            #         "fontSize": "1rem",
                            #         "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                            #         "lineHeight": "1.5",
                            #     },
                            # ),
                            
                            # Toggle Switch Container
                            html.Div(
                                id="toggle-switch-container",
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "width": "30%",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "gap": "10px",  # Расстояние между буквами и тумблером
                                        },
                                        children=[
                                            html.Div(
                                                "Drawings",  # Левый текст
                                                style={
                                                    "fontSize": "1rem",
                                                    "fontWeight": "bold",
                                                    "color": "#2196F3",  # Цвет буквы
                                                },
                                            ),
                                            ToggleSwitch(
                                                id="toggle-switch",
                                                value=False,  # Начальное значение
                                                style={"margin": "0 auto"},
                                                color="#2196F3",  # Цвет тумблера
                                            ),
                                            html.Div(
                                                "Modeling",  # Правый текст
                                                style={
                                                    "fontSize": "1rem",
                                                    "fontWeight": "bold",
                                                    "color": "#2196F3",  # Цвет буквы
                                                },
                                            ),
                                        ],
                                    ),
                                    html.Label(
                                        "",
                                        style={
                                            "marginLeft": "10px",
                                            "fontSize": "1rem",
                                        },
                                    ),
                                ],
                            ),

                            
                            # Interval Buttons
                            html.Div(
                                id="interval-buttons-container",  # Container for interval buttons
                                style={
                                    "display": "flex",
                                    "gap": "10px",
                                    "width": "30%",
                                    "alignItems": "center",
                                },
                                children=[
                                    html.Button(
                                        "D",
                                        id="interval-day",  # Button for daily interval
                                        n_clicks=0,
                                        style={
                                            "padding": "10px 20px",
                                            "borderRadius": "8px",
                                            "background": "#4CAF50",
                                            "color": "#fff",
                                            "fontWeight": "bold",
                                            "border": "none",
                                            "cursor": "pointer",
                                            "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                                        },
                                    ),
                                    html.Button(
                                        "W",
                                        id="interval-week",  # Button for weekly interval
                                        n_clicks=0,
                                        style={
                                            "padding": "10px 20px",
                                            "borderRadius": "8px",
                                            "background": "#2196F3",
                                            "color": "#fff",
                                            "fontWeight": "bold",
                                            "border": "none",
                                            "cursor": "pointer",
                                            "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                                        },
                                    ),
                                    html.Button(
                                        "M",
                                        id="interval-month",  # Button for monthly interval
                                        n_clicks=0,
                                        style={
                                            "padding": "10px 20px",
                                            "borderRadius": "8px",
                                            "background": "#FF5722",
                                            "color": "#fff",
                                            "fontWeight": "bold",
                                            "border": "none",
                                            "cursor": "pointer",
                                            "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                                        },
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Toggle Complexity Checkbox
                    html.Div(
                        id="toggle-complexity-container",  # Container for toggle complexity
                        style={"marginBottom": "15px"},
                        children=[
                            dcc.Checklist(
                                id="toggle-complexity",  # Checkbox to toggle complexity
                                options=[
                                    {"label": "Показывать сложность", "value": "show_complexity"}
                                ],
                                value=["show_complexity"],
                                style={"fontSize": "1rem"},
                            ),
                        ],
                    ),

                    # Line Graph
                    dcc.Graph(
                        id="line-graph",  # Line graph for visualization
                        style={"height": "100%", "width": "100%"},
                    ),
                ],
            ),

            # Right Dashboard Section
            html.Div(
                id="right-dashboard-container",  # Right dashboard section
                style={
                    "position": "relative",
                    "width": "35%",
                    "display": "flex",
                    "flexDirection": "column",
                    "background": "#ffffff",
                    "padding": "20px",
                    "borderRadius": "15px",
                    "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                    "alignItems": "center",
                    "maxHeight": "95vh",
                    "gap": "15px",

                    # "marginLeft": "20px",
                    "maxHeight": "100vh",
                },
                children=[
                    html.Div(
                        id="right-background-frame",  # Background frame for right section
                        style={
                            "position": "absolute",
                            "top": "-15px",
                            "left": "-15px",
                            "right": "-15px",
                            "bottom": "-15px",
                            "zIndex": "-1",
                            "borderRadius": "20px",
                            "background": "#f9f9f9",
                            "boxShadow": "0 8px 20px rgba(0, 0, 0, 0.2)",
                        },
                    ),
                    # Toggle Table Checklist
                    html.Div(
                        id="toggle-table-container",  # Container for table toggle
                        style={
                            "marginBottom": "15px",
                            "background": "#f9f9f9",
                        },
                        children=[
                            dcc.Checklist(
                                id="toggle-table",  # Checkbox to toggle table
                                options=[
                                    {"label": "Показывать таблицу специалистов", "value": "show_table"}
                                ],
                                value=["show_table"],
                                style={"fontSize": "1rem"},
                            ),
                        ],
                    ),

                    # Pie Chart and Table Container
                    html.Div(
                        id="pie-chart-table-container",  # Container for pie chart and table
                        style={
                            "width": "100%",
                            "maxHeight": "70vh",  # Limit max height
                            "background": "#f9f9f9",
                            # "marginTop": "1px",  # Отступ сверху в пикселях
                            "padding": "0 15px 15px", 
                            "borderRadius": "15px",
                            # "marginBottom": "20px",
                            "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                            "overflow": "auto",  # Enable scrolling if content exceeds max height
                        },
                        children=[
                            # Pie Chart
                            dcc.Graph(
                                id="pie-chart",  # Pie chart for visualization
                                # figure=pie_fig,
                                style={"height": "100%", "width": "100%"},
                            ),
                            # Specialist Table
                            html.Div(
                                id="specialist-table-container",  # Container for specialist table
                                style={
                                    "height": "100%", 
                                    "width": "100%",
                                    "background": "#f9f9f9",
                                    "marginTop": "5px",  # Отступ сверху
                                    "padding": "15px",  # Внутренний отступ
                                    "borderRadius": "10px",  # Скругление углов
                                    "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",  # Тень
                                },
                                children=[
                                    # Заголовок таблицы
                                    dcc.Markdown(
                                        "### Список специалистов и их вклад",  # Table title
                                        style={
                                            "marginTop": "0",  # Убран лишний отступ сверху
                                            "marginBottom": "10px",  # Отступ снизу
                                            "fontSize": "1.25rem",  # Размер шрифта
                                            "fontWeight": "bold",  # Полужирный шрифт
                                            "textAlign": "left",  # Выравнивание текста
                                        },
                                    ),
                                    # Таблица данных
                                    dash_table.DataTable(
                                        id="specialist-table",  # ID таблицы
                                        columns=[
                                            {"name": "ФИО", "id": "name"},       # Специалист
                                            {"name": "Σm", "id": "mass"},        # Суммарная масса (т)
                                            {"name": "Σч", "id": "completed_drawings"},        # Суммарная чертежи (кол-во)
                                            {"name": "Σt", "id": "total_hours"}, # Суммарное время (ч)
                                            {"name": "Pₘ", "id": "plan_mass"},   # Плановая масса (т)
                                            {"name": "Tk%", "id": "tekla_percentage"},   # Плановая масса (т)
                                        ],
                                        style_table={"width": "100%"},  # Стиль таблицы
                                        style_cell={
                                            "textAlign": "left",
                                            "padding": "10px",
                                            "border": "1px solid #ddd",
                                            "fontSize": "1rem",
                                            "fontFamily": "Arial, sans-serif",
                                        },
                                        style_header={
                                            "fontWeight": "bold",
                                            "backgroundColor": "#f4f4f4",
                                            "borderBottom": "2px solid #ddd",
                                        },
                                        css=[
                                            {
                                                "selector": "th.dash-header div.column-header-name",
                                                "rule": "display: flex; align-items: center; justify-content: flex-start; gap: 10px;",
                                            },
                                        ],
                                        data=[],  # Данные загружаются динамически
                                        page_size=5,  # Максимум 9 строк на странице
                                        style_as_list_view=True,
                                        sort_action="native",  # Возможность сортировки
                                        sort_mode="single",  # Сортировка по одному столбцу
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Progress Bar Container
                    html.Div(
                        id="progress-bar-container",  # Container for progress bar
                        style={
                            "width": "100%",
                            # "height": "100px",  # Fixed height to stabilize
                            "background": "#f9f9f9",
                            "padding": "15px",
                            "borderRadius": "15px",
                            "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                            # "position": "absolute",  # Keeps it independent
                            "bottom": "20px",  # Positioned relative to parent
                        },
                        children=[
                            html.Div(
                                "Прогресс выполнения",  # Progress bar title
                                style={
                                    "fontSize": "1.1rem",
                                    "fontWeight": "bold",
                                    "textAlign": "center",
                                    "color": "#555",
                                    "marginBottom": "10px",
                                },
                            ),
                            html.Div(
                                style={
                                    "width": "100%",
                                    "height": "30px",
                                    "background": "#f9f9f9",
                                    "borderRadius": "15px",
                                    "overflow": "hidden",
                                    "boxShadow": "inset 0 2px 4px rgba(0, 0, 0, 0.1)",
                                },
                                children=html.Div(
                                    id="progress-bar",  # Actual progress bar
                                    style={
                                        "width": "75%",  # Dynamic width based on progress
                                        "height": "100%",
                                        "background": "linear-gradient(90deg, #4CAF50, #8BC34A)",
                                        "borderRadius": "15px",
                                    },
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
    
    return layout