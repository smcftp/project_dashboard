from dash import dcc, html, dash_table, callback_context
from dash_daq import ToggleSwitch
import plotly.graph_objects as go

import database.db as database

from services.project_service import get_project_list

def create_main_layout():
    
    db = next(database.get_db())
    
    main_pad_color = "#ebebeb"

    layout = html.Div(
        # Main container style
        style={
            "height": "100vh",
            'width': '100%',
            "display": "flex",
            'flexDirection': 'column',
            # "alignItems": "flex-start",
            # "justifyContent": "flex-start",
            "background": "#ffffff",
            # "padding": "20px",
            "overflow": "hidden",
            "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
            # "maxHeight": "100vh",
            "gap": "1%",
        },
        children=[
            # State for table visibility
            dcc.Store(
                id="store-show-table",  # State store for table visibility
                data={"show_table": True}
            ),
            
            html.Div(
                id="header-dashboard-container",  # Left dashboard section
                style={
                    # "position": "relative",
                    "width": "100%",
                    "display": "flex",
                    "flexDirection": "column",
                    # "alignItems": "flex-start",
                    "background": main_pad_color,
                    # "padding": "0.5%",
                    # "padding": "5px",
                    "margin": "0.5% 0 0 0",
                    "borderRadius": "15px",
                    # "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                    # "maxHeight": "15vh",
                    "height": "5vh",
                    # 'height': '15%',
                },
                children=[
                    html.H2(
                        id="dashboard-title",  # Title of the dashboard
                        children="Интерактивная аналитика",
                        style={
                            "position": "relative",
                            "textAlign": "left",
                            "color": "#333",
                            "fontSize": "2rem",
                            "fontWeight": "bold",
                            # "marginBottom": "20px",
                            "margin": "0 0 0 2%",  # Убираем стандартные отступы
                            "textShadow": "1px 1px 3px rgba(0, 0, 0, 0.1)",
                        },
                    ),
                ],
            ),
            
            html.Div(
                id="body-dashboard-container",  # Left dashboard section
                style={
                    "position": "relative",
                    "width": "100%",
                    "display": "flex",
                    "flexDirection": "row",
                    # "alignItems": "flex-start",
                    "background": "#ffffff",
                    # "padding": "20px",
                    "borderRadius": "15px",
                    "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                    "maxHeight": "100vh",
                    'height': '90vh',
                    # "flex": "1",
                    "gap": "1%",
                },
                children=[
                    # Left Dashboard Section
                    html.Div(
                        id="left-dashboard-container",  # Left dashboard section
                        style={
                            # "position": "relative",
                            "width": "60%",
                            'display': 'flex',
                            "flexDirection": "column",
                            "gap": "2%",
                            # "alignItems": "flex-start",
                            "background": "#ffffff",
                            # "padding": "20px",
                            "borderRadius": "15px",
                            "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                            # "maxHeight": "85vh",
                            # "maxHeight": "100vh",
                            'flexShrink': 0,  # Не сжимать
                        },
                        children=[
                            html.Div(
                                id="left-background-frame",  # Background frame for left section
                                style={
                                    "display": "flex",  # Используем flexbox
                                    "flexDirection": "row",  # Размещаем элементы в ряд (горизонтально)
                                    "justifyContent": "space-between",  # Равномерное распределение
                                    "alignItems": "stretch",  # Дочерние контейнеры заполняют высоту родителя
                                    "width": "100%",  # Родитель заполняет всю ширину
                                    "height": "15%",  # Фиксированная высота родителя (можно сделать 100vh)
                                    # "border": "2px solid black",  # Для наглядности
                                    "background": "#ffffff",
                                    # "padding": "10px",
                                    "gap": "1%",
                                },
                                children=[
                                    html.Div(
                                        id="total_spent_money",  # Button for daily interval
                                        style={
                                            
                                            "flex": "1",
                                            "background": "#FF5722",  # Оранжевый фон
                                            "background": main_pad_color,
                                            "color": "#fff",
                                            "color": "black",
                                            "display": "flex",
                                            "alignItems": "center",
                                            "justifyContent": "center",
                                            "fontSize": "40px",
                                            "borderRadius": "10px",
                                            "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                                        },
                                    ),
                                    html.Div(
                                        id="total_spent_hours",  # Button for weekly interval
                                         style={
                                            
                                            "flex": "1",  # Равномерное распределение ширины
                                            "background": "#4CAF50",  # Зеленый фон
                                            "background": main_pad_color,
                                            "color": "black",
                                            "display": "flex",
                                            "alignItems": "center",
                                            "justifyContent": "center",
                                            "fontSize": "40px",
                                            "borderRadius": "10px",
                                            "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                                        },
                                    ),
                                    html.Div(
                                        id="total_complexity",  # Button for monthly interval
                                        style={
                                            
                                            "flex": "1",
                                            "background": "#2196F3",  # Синий фон
                                            "background": main_pad_color,
                                            "color": "black",
                                            "display": "flex",
                                            "alignItems": "center",
                                            "justifyContent": "center",
                                            "fontSize": "40px",
                                            "borderRadius": "10px",
                                            "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                                        },
                                    ),
                                ],
                            ),
                            # html.H1(
                            #     id="dashboard-title",  # Title of the dashboard
                            #     children="Интерактивная аналитика",
                            #     style={
                            #         "textAlign": "left",
                            #         "color": "#333",
                            #         "fontSize": "2rem",
                            #         "fontWeight": "bold",
                            #         # "marginBottom": "20px",
                            #         "textShadow": "1px 1px 3px rgba(0, 0, 0, 0.1)",
                            #     },
                            # ),

                            # Dropdown and Interval Selection Container
                            html.Div(
                                id="dropdown-and-interval-container",  # Container for dropdown and interval buttons
                                style={
                                    "display": "flex",
                                    "flexDirection": "row",
                                    "justifyContent": "space-between",
                                    "alignItems": "center",
                                    "width": "100%",
                                    "hight": "15%",
                                    "background": main_pad_color,
                                    "padding": "15px 20px",
                                    "borderRadius": "10px",
                                    "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
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
                                            # "padding": "0.1%",
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
                                            # "padding": "0.1%",
                                            "border": "1px solid #ddd",
                                            "borderRadius": "8px",
                                            "background": "#f9f9f9",
                                            "fontSize": "1rem",
                                            "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                                            "lineHeight": "1.5",
                                        },
                                    ),
                                    
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
                            # html.Div(
                            #     id="toggle-complexity-container",  # Container for toggle complexity
                            #     style={
                            #         "marginBottom": "15px",
                            #         "height": "1%", 
                            #         "maxHeight": "1%"
                            #     },
                            #     children=[
                            #         dcc.Checklist(
                            #             id="toggle-complexity",  # Checkbox to toggle complexity
                            #             options=[
                            #                 {"label": "Показывать сложность", "value": "show_complexity"}
                            #             ],
                            #             value=["show_complexity"],
                            #             style={"fontSize": "1rem"},
                            #         ),
                            #     ],
                            # ),
                            
                            
                            html.Div(
                                id="line-chart-container",
                                style={
                                    # "marginBottom": "15px",
                                    "height": "50%",  # Высота 10%
                                    # "maxHeight": "50%",
                                    "display": "flex",
                                    "background": "black",
                                    "overflow": "auto",
                                },
                                children=[
                                    # Line Graph
                                    dcc.Graph(
                                        id="line-graph",  # Line graph for visualization
                                        style={
                                            "height": "100%", 
                                            "width": "100%",
                                            # "display": "flex",
                                            # "flexDirection": "row",
                                            # "justifyContent": "space-between",
                                            # "alignItems": "center",
                                            "background": main_pad_color,
                                            # "padding": "15px 20px",
                                            "borderRadius": "10px",
                                            "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.05)",
                                            "boxSizing": "border-box",
                                        },
                                    ),
                                ],
                            ),
                            
                            
                            html.Div(
                                id="complexity-chart-container",
                                style={
                                    # "marginBottom": "15px",
                                    "height": "15%",  # Высота 10%
                                    # "maxHeight": "15%",
                                    "display": "flex",
                                    "background": "black",
                                    "overflow": "auto",
                                },
                                children=[
                                    dcc.Graph(
                                        id="complexity-chart",
                                        style={
                                            "height": "100%", 
                                            "width": "100%",
                                            # "display": "flex",
                                            # "flexDirection": "row",
                                            # "justifyContent": "space-between",
                                            # "alignItems": "center",
                                            # "width": "100%",
                                            "background": "red",
                                            # "padding": "15px 20px",
                                            # "borderRadius": "10px",
                                            # "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.05)",
                                            # "boxSizing": "border-box",
                                        },
                                        # figure=fig_complexity,
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # Right Dashboard Section
                    html.Div(
                        id="right-dashboard-container",  # Right dashboard section
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "10px",  # Обеспечивает отступ между дочерними элементами
                            "width": "36%",
                            "position": "relative",  # Фиксируем проблему с исчезновением right-background-frame
                            "background": "#ffffff",
                            "borderRadius": "15px",
                            "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                            "alignItems": "center",
                            "marginLeft": "20px",
                            "maxHeight": "100vh",
                        },
                        children=[
                            html.Div(
                                id="right-background-frame",  # Background frame for right section
                                style={
                                    "position": "relative",  # Убедимся, что позиционируется относительно родителя
                                    # "right": "-15px",
                                    # "bottom": "-15px",
                                    "zIndex": "1",
                                    "borderRadius": "20px",
                                    "background": "#ffffff",
                                    "display": "flex",
                                    # "padding": "10px",
                                    "justifyContent": "center",
                                    "gap": "10px",
                                    "width": "100%",
                                },
                                children=[
                                    dcc.Input(
                                        id="input-number",
                                        type="number",  # Только числа
                                        placeholder="Введите число...",
                                        style={
                                            "flex": "1",  # Растягивается на всю доступную ширину
                                            # "padding": "10px",
                                            "borderRadius": "5px",
                                            "border": "none",
                                            "textAlign": "center",
                                            "width": "100%",  # Обеспечивает полную ширину внутри flex-контейнера
                                            "background": main_pad_color,
                                            "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                                        },
                                    ),
                                    dcc.DatePickerSingle(
                                        id="input-date",
                                        # placeholder="Выберите дату",
                                        display_format="DD.MM.YYYY",
                                        style={
                                            "flex": "1",
                                            "width": "100%",
                                            "height": "100%",  # Добавляем высоту для соответствия родителю
                                            "padding": "0",  # Убираем лишний внутренний отступ
                                            "borderRadius": "5px",
                                            "border": "none",
                                            "background": "white",
                                            "textAlign": "center",
                                            "display": "block",  # Убираем возможные inline-эффекты
                                            "background": main_pad_color,
                                            "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
                                        },
                                    ),
                                ],
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
                                    "height": "400px",
                                    # "maxHeight": "70vh",  # Limit max height
                                    "minHeight": "400px",
                                    "background": main_pad_color,
                                    # "marginTop": "1px",  # Отступ сверху в пикселях
                                    # "padding": "0 15px 15px", 
                                    "borderRadius": "15px",
                                    # "marginBottom": "20px",
                                    "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                                    "overflow": "auto",  # Enable scrolling if content exceeds max height
                                },
                                children=[
                                    # Pie Chart
                                    dcc.Graph(
                                        id="bar-chart",  # Гистограмма для визуализации
                                        # figure=create_horizontal_bar_chart(df_pie),  # Предполагается, что функция create_horizontal_bar_chart создает график
                                        style={
                                            # "display": "flex",
                                            # 'flexShrink': 0,
                                            "height": "100%", 
                                            "width": "100%",
                                            "maxHeight": "70vh",
                                            "minHeight": "400px",
                                            "background": main_pad_color,
                                        },
                                    ),
                                    # Specialist Table
                                    html.Div(
                                        id="specialist-table-container",  # Container for specialist table
                                        style={
                                            # "height": "100%", 
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
                                                # columns=[
                                                #     {"name": "ФИО", "id": "name"},       # Специалист
                                                #     {"name": "Σm", "id": "mass"},        # Суммарная масса (т)
                                                #     {"name": "Σч", "id": "completed_drawings"},        # Суммарная чертежи (кол-во)
                                                #     {"name": "Σt", "id": "total_hours"}, # Суммарное время (ч)
                                                #     {"name": "Pₘ", "id": "plan_mass"},   # Плановая масса (т)
                                                #     {"name": "Tk%", "id": "tekla_percentage"},   # Плановая масса (т)
                                                # ],
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
                                                tooltip_header={  # Подсказки для заголовков
                                                    # "name": "Фамилия, Имя, Отчество специалиста",
                                                    "mass": "Суммарная масса в тоннах",
                                                    "completed_drawings": "Общее количество созданных чертежей",
                                                    "total_hours": "Суммарное рабочее время в ВС в часах",
                                                    "plan_mass": "Плановая масса в тоннах",
                                                    "tekla_percentage": "% времени в Tekla от общего",
                                                },
                                                tooltip_delay=500,  # Задержка перед появлением
                                                tooltip_duration=None,  # Подсказка будет показываться без ограничения по времени
                                                css=[
                                                    {
                                                        "selector": "th",
                                                        "rule": "cursor: help;",
                                                    },
                                                    {
                                                        "selector": ".dash-table-tooltip",
                                                        "rule": """
                                                            background-color: white;
                                                            color: rgba(0, 0, 0, 0.8);
                                                            font-size: 14px;
                                                            padding: 8px;
                                                            border-radius: 5px;
                                                            white-space: normal;
                                                            width: fit-content;
                                                            word-break: normal;
                                                        """,
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
                                id="progress-bar-container-drawing",  # Container for progress bar
                                style={
                                    "width": "100%",
                                    "height": "30%",  # Исправлена ошибка в height
                                    "background": main_pad_color,
                                    "borderRadius": "15px",
                                    "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                                    "bottom": "20px",  # Positioned relative to parent
                                },
                                children=[
                                    html.Div(
                                        "Прогресс выполнения чертежей",  # Progress bar title
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
                                            id="progress-bar-drawing",  # Actual progress bar
                                            style={
                                                "width": "0%",  # Изначально ширина 0, потом будет обновляться
                                                "height": "100%",
                                                "background": "linear-gradient(90deg, #4CAF50, #8BC34A)",
                                                "borderRadius": "15px",
                                            },
                                        ),
                                    ),
                                ],
                            ),
                            
                            # Progress Bar Container
                            html.Div(
                                id="progress-bar-container-modeling",  # Container for progress bar
                                style={
                                    "width": "100%",
                                    "height": "30%",  # Исправлена ошибка в height
                                    "background": main_pad_color,
                                    "borderRadius": "15px",
                                    "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                                    "bottom": "20px",  # Positioned relative to parent
                                },
                                children=[
                                    html.Div(
                                        "Прогресс выполнения моделирования",  # Progress bar title
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
                                            id="progress-bar-modeling",  # Actual progress bar
                                            style={
                                                "width": "0%",  # Изначально ширина 0, потом будет обновляться
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
            ),

            
        ],
    )
    
    return layout
