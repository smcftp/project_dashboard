from dash import dash, Input, Output, callback_context
import plotly.graph_objects as go
from decimal import Decimal


from services.project_service import get_project_list, get_time_by_chapter_for_title, get_total_time_money_complexity_for_title
from services.drawing_service import get_data_for_project, get_drawing_data_for_project, get_completed_mass_for_project_mod, get_completed_mass_for_project_dr
from services.executor_service import get_executors_data_by_project

import database.db as database
import database.models as models
import pandas as pd
from config import app

# Подготовка данных для интервалов
def transform_date_column(df: pd.DataFrame, interval: str, toggle_switch_m_or_d: bool) -> pd.DataFrame:
    """
    Преобразует столбец 'Дата' в datetime и группирует данные по заданному интервалу.

    :param df: Исходный DataFrame.
    :param interval: Интервал группировки ('week', 'month' или 'day').
    :param toggle_switch_m_or_d: Флаг для выбора типа агрегации.
    :return: Преобразованный DataFrame.
    """
    df = df.copy()
    df["Дата"] = pd.to_datetime(df["Дата"], errors="coerce")

    if interval == "week":
        df["Группировка"] = df["Дата"].dt.to_period("W").apply(lambda r: r.start_time)
    elif interval == "month":
        df["Группировка"] = df["Дата"].dt.to_period("M").apply(lambda r: r.start_time)
    else:
        df["Группировка"] = df["Дата"]

    if interval in ["week", "month"]:
        agg_dict = {"Всего чертежей": "sum"} if not toggle_switch_m_or_d else {
            "Масса": "sum",
            "Сложность": "mean",
            "Плановая масса": "sum"
        }
        df = df.groupby("Группировка").agg(agg_dict).reset_index().rename(columns={"Группировка": "Дата"})

    return df

# Функция для получения данных для графика
def fetch_data_for_graph(db_session, selected_title, toggle_switch_m_or_d):
    try:
        # Возвращаем данные в зависимости от состояния переключателя
        if toggle_switch_m_or_d:
            return get_data_for_project(db=db_session, title_id=selected_title)
        return get_drawing_data_for_project(db=db_session, title_id=selected_title)
    except Exception as e:
        print(f"Error fetching data for graph: {e}")
        return pd.DataFrame()  # Возвращаем пустой DataFrame в случае ошибки

# Функция для создания круговой диаграммы
def create_pie_chart(df_pie):
    try:
        labels = df_pie["chapter_name"].dropna().astype(str).tolist()
        values = df_pie["percentage"].dropna().astype(float).tolist()
        return go.Figure(
            data=[go.Pie(
                labels=labels, 
                values=values, 
                hole=0.4,
                textinfo="none",  
                hoverinfo="label+percent"
            )],
            layout=go.Layout(
                showlegend=False,  
                title="Категории времязатрат по главам",
                title_x=0.5,
                title_y=0.9,
                plot_bgcolor="rgba(240, 248, 255, 0.8)",  
                paper_bgcolor="#f9f9f9",  
            )
        )
    except Exception as e:
        print(f"Error creating pie chart: {e}")
        return go.Figure()  # Возвращаем пустую фигуру в случае ошибки

# Создание горизонтального бар-чарт сперевернутой осью Y
def create_horizontal_bar_chart(df_pie):
    try:
        labels = df_pie["chapter_name"].dropna().astype(str).tolist()
        values = df_pie["percentage"].dropna().astype(float).tolist()
        
        return go.Figure(
            data=[go.Bar(
                x=values, 
                y=labels,  
                orientation="h",
                
                # Вариант с отображенеим в сноске
                # text=None,  # Убираем постоянный текст
                # hoverinfo="x+y",  # Отображаем только значения при наведении
                # hovertemplate="<b>%{y}</b><br>Процент: %{x:.0f}%",  # Форматирование текста в сноске
                
                # Вариант с отображением сразу на графике
                text=["<b>" + label + "</b><br>Процент: " + str(round(value)) + "%" for label, value in zip(labels, values)],  # Округляем до целого числа
                hoverinfo="none",  # Отображаем только text при наведении
                hoverlabel=dict(
                    bgcolor="#f9f9f9",  # Цвет фона сноски (полупрозрачный черный)
                    font=dict(
                        family="Arial",  # Шрифт текста
                        size=14,  # Размер шрифта
                        color="rgba(0,0,0,0.7)"  # Цвет шрифта
                    ),
                    bordercolor="rgba(0,0,0,0.7)",  # Цвет рамки сноски
                    align="auto"  # Выравнивание текста
                ),
                marker=dict(
                    color=values,  # Используем значения для задания цвета
                    colorscale=[[0, '#4CAF50'], [1, '#8BC34A']],  # Используем градиент
                    # colorbar=dict(title="Процент")  # Добавляем шкалу цвета
                ),    # Настроенный цвет
                name=" ",  # Указываем имя для следа, чтобы убрать "trace0"
            )],
            layout=go.Layout(
                title="Категории времязатрат по главам",
                title_x=0.5,
                xaxis_title="Процент",
                yaxis_title="Глава",
                # xaxis=dict(showticklabels=False),  # Убираем значения оси X
                yaxis=dict(showticklabels=False),  # Убираем значения оси Y
                showlegend=False,  # Убираем легенду
                plot_bgcolor="#f9f9f9",  # Цвет фона графика
                paper_bgcolor="#f9f9f9"  # Цвет фона всей области
            )
        )
    except Exception as e:
        print(f"Error creating horizontal bar chart: {e}")
        return go.Figure()

# Функция для создания линейного графика
def create_line_graph(df_line, interval, toggle_switch_m_or_d):
    try:
        if not isinstance(df_line, pd.DataFrame):
            raise TypeError("Expected df_line to be a DataFrame")
        if "Дата" not in df_line.columns:
            raise KeyError("Column 'Дата' not found in the DataFrame")

        # Преобразование столбца "Дата" в datetime
        df_line["Дата"] = pd.to_datetime(df_line["Дата"], errors="coerce")
        df_line = transform_date_column(df=df_line, interval=interval, toggle_switch_m_or_d=toggle_switch_m_or_d)
        
        # Создание графика
        line_fig = go.Figure()

        if toggle_switch_m_or_d:
            
            # Добавляем линию массы
            line_fig.add_trace(go.Scatter(
                x=df_line["Дата"], y=df_line["Масса"],
                mode="lines+markers", name="Масса",
                line=dict(color="#3b5998", width=3),
                marker=dict(color="#4CAF50", size=8),
            ))

            # Добавляем линию плановой массы
            line_fig.add_trace(go.Scatter(
                x=df_line["Дата"], y=df_line["Плановая масса"],
                mode="lines+markers", name="Плановая масса",
                line=dict(color="#FFA500", width=3, dash="dash"),
                marker=dict(color="#FFA500", size=8),
            ))

            # Добавляем закрашенные области
            for i in range(len(df_line) - 1):
                x_fill = [df_line["Дата"][i], df_line["Дата"][i+1], df_line["Дата"][i+1], df_line["Дата"][i]]
                y_fill = [df_line["Масса"][i], df_line["Масса"][i+1], df_line["Плановая масса"][i+1], df_line["Плановая масса"][i]]
                color = "green" if df_line["Масса"][i] > df_line["Плановая масса"][i] else "red"

                line_fig.add_trace(go.Scatter(
                    x=x_fill, y=y_fill, fill='toself', mode='none',
                    fillcolor=color, opacity=0.5,
                    showlegend=False,  # Отключаем отображение области в легенде
                ))

            # Обновляем layout
            line_fig.update_layout(
                yaxis=dict(tickfont=dict(color="#4CAF50")),
                yaxis2=dict(tickfont=dict(color="#FF5722"), overlaying="y", side="right"),
                hovermode="x unified",
                plot_bgcolor="#f9f9f9",
                paper_bgcolor="#f9f9f9",
                margin=dict(l=20, r=20, t=30, b=20),
                autosize=True,
                legend=dict(title="Показатели", orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            )

            # if "show_complexity" in toggle_complexity:
            #     line_fig.add_trace(go.Scatter(
            #         x=df_line["Дата"], y=df_line["Сложность"],
            #         mode="lines+markers", name="Сложность",
            #         line=dict(color="#FF5722", width=2),
            #         marker=dict(color="#2196F3", size=6),
            #         yaxis="y2"
            #     ))

            #     line_fig.update_layout(
            #         title=f"Линейный график производительности и сложности ({interval})",
            #         xaxis_title="Дата",
            #         yaxis=dict(title="Масса", tickfont=dict(color="#4CAF50")),
            #         yaxis2=dict(title="Сложность", tickfont=dict(color="#FF5722"), overlaying="y", side="right"),
            #         hovermode="x unified",
            #         plot_bgcolor="#f9f9f9",
            #         paper_bgcolor="#f9f9f9",
            #         legend=dict(title="Показатели", orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            #     )
        else:
            # Добавляем линии для "Всего чертежей"
            # line_fig.add_trace(go.Scatter(
            #     x=df_line["Дата"], y=df_line["Всего чертежей"],
            #     mode="lines+markers", name="Чертежи",
            #     line=dict(color="#3b5998", width=3),
            #     marker=dict(color="#4CAF50", size=8),
            #     yaxis="y1",
            # ))

            # line_fig.update_layout(
            #     title=f"Линейный график количества чертежей ({interval})",
            #     xaxis_title="Дата",
            #     yaxis=dict(title="Чертежи", tickfont=dict(color="#4CAF50")),
            #     hovermode="x unified",
            #     plot_bgcolor="#ebebeb",
            #     paper_bgcolor="#ebebeb",
            #     legend=dict(title="Показатели", orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            #     margin=dict(l=20, r=20, t=30, b=20),
            #     autosize=True,
            # )
            
            # Добавляем линию массы
            line_fig.add_trace(go.Scatter(
                x=df_line["Дата"], y=df_line["Масса"],
                mode="lines+markers", name="Масса",
                line=dict(color="#3b5998", width=3),
                marker=dict(color="#4CAF50", size=8),
            ))

            # Добавляем линию плановой массы
            line_fig.add_trace(go.Scatter(
                x=df_line["Дата"], y=df_line["Плановая масса"],
                mode="lines+markers", name="Плановая масса",
                line=dict(color="#FFA500", width=3, dash="dash"),
                marker=dict(color="#FFA500", size=8),
            ))

            # Добавляем закрашенные области
            for i in range(len(df_line) - 1):
                x_fill = [df_line["Дата"][i], df_line["Дата"][i+1], df_line["Дата"][i+1], df_line["Дата"][i]]
                y_fill = [df_line["Масса"][i], df_line["Масса"][i+1], df_line["Плановая масса"][i+1], df_line["Плановая масса"][i]]
                color = "green" if df_line["Масса"][i] > df_line["Плановая масса"][i] else "red"

                line_fig.add_trace(go.Scatter(
                    x=x_fill, y=y_fill, fill='toself', mode='none',
                    fillcolor=color, opacity=0.5,
                    showlegend=False,  # Отключаем отображение области в легенде
                ))

            # Обновляем layout
            line_fig.update_layout(
                yaxis=dict(tickfont=dict(color="#4CAF50")),
                yaxis2=dict(tickfont=dict(color="#FF5722"), overlaying="y", side="right"),
                hovermode="x unified",
                plot_bgcolor="#f9f9f9",
                paper_bgcolor="#f9f9f9",
                margin=dict(l=20, r=20, t=30, b=20),
                autosize=True,
                legend=dict(title="Показатели", orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            )


        return line_fig
    except Exception as e:
        print(f"Error creating line graph: {e}")
        return go.Figure()  # Возвращаем пустую фигуру в случае ошибки


def create_bar_chart(df: pd.DataFrame, interval: int):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Дата"],
        y=df["Сложность"],
        name="Сложность",
        marker_color="#FF5722"
    ))
    
    fig.update_layout(
        title="Сложность по времени",
        # xaxis_title="Дата",
        # yaxis_title="Сложность",
        # height=500,  # Увеличенная высота для лучшей читаемости
        # bargap=0.1,  # Оптимальная ширина столбцов
        yaxis=dict(range=[0, max(df["Сложность"]) + 1]),  # Добавляем отступ по оси Y
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#f9f9f9",
        margin=dict(l=0.1, r=0.1, t=0.1, b=0.1),
        autosize=True
    )
    return fig


# Регистрация колбеков для обновления графиков и таблиц
def register_graph_callbacks(app):
    @app.callback(
        Output("bar-chart", "figure"),
        [Input("title-dropdown", "value")],
    )
    def update_pie_chart(selected_title):
        try:
            if not selected_title:
                return go.Figure().to_dict()

            db = next(database.get_db())
            df_pie = get_time_by_chapter_for_title(db=db, title_id=selected_title)
            # return create_pie_chart(df_pie).to_dict()
            return create_horizontal_bar_chart(df_pie).to_dict()

        except Exception as e:
            print(f"Error updating pie chart: {e}")
            return go.Figure().to_dict()

    @app.callback(
        Output("line-graph", "figure"),
        [
            Input("title-dropdown", "value"),
            Input("interval-day", "n_clicks"),
            Input("interval-week", "n_clicks"),
            Input("interval-month", "n_clicks"),
            # Input("toggle-complexity", "value"),
            Input("toggle-table", "value"),
            Input("toggle-switch", "value"),
        ],
    )
    def update_graph(selected_title, n_clicks_day, n_clicks_week, n_clicks_month, toggle_table, toggle_switch_m_or_d):
        try:
            ctx = callback_context
            interval = "day"  # default value
            if ctx.triggered:
                button_id = ctx.triggered[0]["prop_id"].split(".")[0]
                interval = button_id.split("-")[1]

            db = next(database.get_db())
            df_line = fetch_data_for_graph(db, selected_title, toggle_switch_m_or_d)

            if df_line.empty:
                return go.Figure().to_dict()

            return create_line_graph(df_line, interval, toggle_switch_m_or_d).to_dict()
        except Exception as e:
            print(f"Error updating line graph: {e}")
            return go.Figure().to_dict()

    @app.callback(
        Output("store-show-table", "data"),
        Input("toggle-table", "value")
    )
    def toggle_table_visibility(toggle_table):
        try:
            return {"show_table": "show_table" in toggle_table}
        except Exception as e:
            print(f"Error toggling table visibility: {e}")
            return {}

    @app.callback(
        Output("bar-chart", "style"),
        Input("store-show-table", "data")
    )
    def update_pie_chart_visibility(store_data):
        try:
            if store_data and "show_table" in store_data and store_data["show_table"]:
                return {"display": "none"}
            # return {"height": "45%", "width": "100%"}
        except Exception as e:
            print(f"Error updating pie chart visibility: {e}")
            # return {"height": "45%", "width": "100%"}

    @app.callback(
        [
            Output("specialist-table", "data"), 
            Output("specialist-table", "columns"),
        ],
        [
            Input("title-dropdown", "value"), 
            Input("toggle-switch", "value"),
        ]
    )
    def update_specialist_table(selected_project, toggle_value):
        try:
            if not selected_project:
                return [], []
            db = next(database.get_db())
            if not db:
                print("Database connection error.")
                return [], []
            df = get_executors_data_by_project(db_session=db, title_id=selected_project)
            if df.empty:
                print("No data found.")
                return [], []
            
            # Определяем, какие колонки показывать
            modeling_columns = [
                {"name": "ФИО", "id": "name"},
                {"name": "Σm", "id": "total_mass_modeling"},
                {"name": "Σч", "id": "completed_drawings"},
            ]
            drawings_columns = [
                {"name": "ФИО", "id": "name"},
                {"name": "Σm", "id": "total_mass_drawing"},
                {"name": "Σt", "id": "total_hours"},
                {"name": "Pₘ", "id": "plan_mass"},
                {"name": "Tk%", "id": "tekla_percentage"},
            ]
            
            return df.to_dict("records"), modeling_columns if toggle_value else drawings_columns
        
        except Exception as e:
            print(f"Error updating specialist table: {e}")
            return []

    @app.callback(
        Output("specialist-table-container", "style"),
        Input("store-show-table", "data")
    )
    def toggle_table_visibility(store_data):
        try:
            if store_data and "show_table" in store_data:
                return {"height": "45%", "width": "100%", "display": "block" if store_data["show_table"] else "none"}
            else:
                return {"height": "45%", "width": "100%", "display": "none"}
        except Exception as e:
            print(f"Error updating table visibility: {e}")
            return {"height": "45%", "width": "100%", "display": "none"}

    @app.callback(
        Output("title-dropdown", "options"),
        Input("project-dropdown", "value")
    )
    def update_titles(project_id):
        if not project_id:
            return []
        db = next(database.get_db())
        titles = db.query(models.Title).filter(models.Title.project_id == project_id).all()
        db.close()
        return [{"label": title.title_name, "value": title.id} for title in titles]
    
    @app.callback(
        Output("total_spent_money", "children"),
        Output("total_spent_hours", "children"),
        Output("total_complexity", "children"),
        Input("title-dropdown", "value"),  # Выбор титула из dropdown
    )
    def update_dashboard(selected_title_id):
        if not selected_title_id:
            return "Нет данных", "Нет данных", "Нет данных"

        db = next(database.get_db())
        data = get_total_time_money_complexity_for_title(db=db, title_id=selected_title_id)
        db.close()
        
        print(data)

        # Вычисляем общую сумму и время
        total_money = round(data["Сумма денег"].sum(), 0)  # Суммируем значения по столбцу
        total_hours = round(data["Общее время (часы)"].sum(), 0)  # Суммируем значения по столбцу
        total_complexity = round(data["Общая сложность"].sum(), 0)  # Суммируем значения по столбцу
        
        print(f"{total_money} BYN", f"{total_hours} ч", f"{total_complexity}⚖️")

        # Возвращаем значения в нужном формате
        return f"{total_money} BYN", f"{total_hours} ч", f"{total_complexity}⚖️"


    # Callback для обновления прогресс бара моделирования на основе введенного значения и данных из БД
    @app.callback(
        Output("progress-bar-modeling", "style"),
        [
            Input("input-number", "value"), 
            Input("input-date", "date"),
            Input("title-dropdown", "value")
        ],
    )
    def update_progress_bar(input_number, input_date, selected_title_id):
        if input_number is not None:
            # Получаем выполненную массу из БД
            db = next(database.get_db())
            completed_mass = get_completed_mass_for_project_mod(db=db, title_id=selected_title_id)
            db.close()
            
            # Расчет прогресса
            max_mass = input_number  # Это максимальная масса из введенного значения
            if max_mass > 0:
                progress_percentage = (Decimal(completed_mass) / Decimal(max_mass)) * 100
            else:
                progress_percentage = 0

            return {
                "width": f"{progress_percentage:.2f}%",  # Динамическое значение
                "height": "100%",
                "background": "linear-gradient(90deg, #4CAF50, #8BC34A)",
                "borderRadius": "15px",
            }
        return dash.no_update
    
    # Callback для обновления прогресс бара чертежей на основе введенного значения и данных из БД
    @app.callback(
        Output("progress-bar-drawing", "style"),
        [
            Input("input-number", "value"), 
            Input("input-date", "date"),
            Input("title-dropdown", "value")
        ],
    )
    def update_progress_bar(input_number, input_date, selected_title_id):
        if input_number is not None:
            # Получаем выполненную массу из БД
            db = next(database.get_db())
            completed_mass, initial_mass = get_completed_mass_for_project_dr(db=db, title_id=selected_title_id)
            db.close()
            
            # Расчет прогресса
            # Это максимальная масса из введенного значения или из БД
            max_mass = input_number if initial_mass == 0 else initial_mass  
            if max_mass > 0:
                progress_percentage = (Decimal(completed_mass) / Decimal(max_mass)) * 100
            else:
                progress_percentage = 0

            return {
                "width": f"{progress_percentage:.2f}%",  # Динамическое значение
                "height": "100%",
                "background": "linear-gradient(90deg, #4CAF50, #8BC34A)",
                "borderRadius": "15px",
            }
        return dash.no_update
    
    @app.callback(
        Output("complexity-chart", "figure"),
        [
            Input("title-dropdown", "value"),
            Input("interval-day", "n_clicks"),
            Input("interval-week", "n_clicks"),
            Input("interval-month", "n_clicks"),
            Input("toggle-switch", "value"),
        ]
        
    )
    def update_complexity_chart(selected_title, n_clicks_day, n_clicks_week, n_clicks_month,toggle_switch_m_or_d):
        try:
            
            ctx = callback_context
            interval = "day"  # default value
            if ctx.triggered:
                button_id = ctx.triggered[0]["prop_id"].split(".")[0]
                interval = button_id.split("-")[1]
            
            db = next(database.get_db())
            df_line = fetch_data_for_graph(db, selected_title, toggle_switch_m_or_d)
            
            df_line = transform_date_column(df=df_line, interval=interval, toggle_switch_m_or_d=toggle_switch_m_or_d)

            if df_line.empty:
                return go.Figure().to_dict()

            return create_bar_chart(df=df_line, interval=interval).to_dict()
        except Exception as e:
            print(f"Error updating complexity chart: {e}")
            return go.Figure().to_dict()
