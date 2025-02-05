from dash import Input, Output, callback_context
import plotly.graph_objects as go
from services.project_service import get_project_list, get_time_by_chapter_for_title
from services.drawing_service import get_data_for_project, get_drawing_data_for_project
from services.executor_service import get_executors_data_by_project
import database.db as database
import database.models as models
import pandas as pd
from config import app

# Функция для получения данных для графика
def fetch_data_for_graph(db_session, selected_title, interval, toggle_switch_m_or_d):
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

# Функция для создания линейного графика
def create_line_graph(df_line, interval, toggle_switch_m_or_d, toggle_complexity):
    try:
        if not isinstance(df_line, pd.DataFrame):
            raise TypeError("Expected df_line to be a DataFrame")
        if "Дата" not in df_line.columns:
            raise KeyError("Column 'Дата' not found in the DataFrame")

        # Преобразование столбца "Дата" в datetime
        df_line["Дата"] = pd.to_datetime(df_line["Дата"], errors="coerce")
        
        if interval == "week":
            df_line["Неделя"] = df_line["Дата"].dt.to_period("W").apply(lambda r: r.start_time)
            group_col = "Неделя"
        elif interval == "month":
            df_line["Месяц"] = df_line["Дата"].dt.to_period("M").apply(lambda r: r.start_time)
            group_col = "Месяц"
        else:
            group_col = "Дата"

        if interval in ["week", "month"]:
            agg_dict = {"Всего чертежей": "sum"} if not toggle_switch_m_or_d else {
                "Масса": "sum",
                "Сложность": "mean",
                "Плановая масса": "sum"
            }
            df_line = df_line.groupby(group_col).agg(agg_dict).reset_index().rename(columns={group_col: "Дата"})
        else:
            df_line = df_line
        
        # Создание графика
        line_fig = go.Figure()

        if toggle_switch_m_or_d:
            # Добавляем линии для различных показателей
            line_fig.add_trace(go.Scatter(
                x=df_line["Дата"], y=df_line["Масса"],
                mode="lines+markers", name="Масса",
                line=dict(color="#3b5998", width=3),
                marker=dict(color="#4CAF50", size=8),
                yaxis="y1"
            ))

            line_fig.add_trace(go.Scatter(
                x=df_line["Дата"], y=df_line["Плановая масса"],
                mode="lines+markers", name="Плановая масса",
                line=dict(color="#FFA500", width=3, dash="dash"),
                marker=dict(color="#FFA500", size=8),
                yaxis="y1"
            ))

            if "show_complexity" in toggle_complexity:
                line_fig.add_trace(go.Scatter(
                    x=df_line["Дата"], y=df_line["Сложность"],
                    mode="lines+markers", name="Сложность",
                    line=dict(color="#FF5722", width=2),
                    marker=dict(color="#2196F3", size=6),
                    yaxis="y2"
                ))

                line_fig.update_layout(
                    title=f"Линейный график производительности и сложности ({interval})",
                    xaxis_title="Дата",
                    yaxis=dict(title="Масса", tickfont=dict(color="#4CAF50")),  # Fixed here
                    yaxis2=dict(title="Сложность", tickfont=dict(color="#FF5722"), tickfont=dict(color="#FF5722"),
                                overlaying="y", side="right"),
                    hovermode="x unified",
                    plot_bgcolor="#f9f9f9",
                    paper_bgcolor="#f9f9f9",
                    legend=dict(title="Показатели", orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                )
        else:
            # Добавляем линии для "Всего чертежей"
            line_fig.add_trace(go.Scatter(
                x=df_line["Дата"], y=df_line["Всего чертежей"],
                mode="lines+markers", name="Чертежи",
                line=dict(color="#3b5998", width=3),
                marker=dict(color="#4CAF50", size=8),
                yaxis="y1"
            ))

            line_fig.update_layout(
                title=f"Линейный график количества чертежей ({interval})",
                xaxis_title="Дата",
                yaxis=dict(title="Чертежи", tickfont=dict(color="#4CAF50"), tickfont=dict(color="#4CAF50")),
                hovermode="x unified",
                plot_bgcolor="#f9f9f9",
                paper_bgcolor="#f9f9f9",
                legend=dict(title="Показатели", orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            )

        return line_fig
    except Exception as e:
        print(f"Error creating line graph: {e}")
        return go.Figure()  # Возвращаем пустую фигуру в случае ошибки

# Регистрация колбеков для обновления графиков и таблиц
def register_graph_callbacks(app):
    @app.callback(
        Output("pie-chart", "figure"),
        [Input("title-dropdown", "value")],
    )
    def update_pie_chart(selected_title):
        try:
            if not selected_title:
                return go.Figure().to_dict()

            db = next(database.get_db())
            df_pie = get_time_by_chapter_for_title(db=db, title_id=selected_title)
            return create_pie_chart(df_pie).to_dict()
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
            Input("toggle-complexity", "value"),
            Input("toggle-table", "value"),
            Input("toggle-switch", "value"),
        ],
    )
    def update_graph(selected_title, n_clicks_day, n_clicks_week, n_clicks_month, toggle_complexity, toggle_table, toggle_switch_m_or_d):
        try:
            ctx = callback_context
            interval = "day"  # default value
            if ctx.triggered:
                button_id = ctx.triggered[0]["prop_id"].split(".")[0]
                interval = button_id.split("-")[1]

            db = next(database.get_db())
            df_line = fetch_data_for_graph(db, selected_title, interval, toggle_switch_m_or_d)

            if df_line.empty:
                return go.Figure().to_dict()

            return create_line_graph(df_line, interval, toggle_switch_m_or_d, toggle_complexity).to_dict()
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
        Output("pie-chart", "style"),
        Input("store-show-table", "data")
    )
    def update_pie_chart_visibility(store_data):
        try:
            if store_data["show_table"]:
                return {"display": "none"}
            return {"height": "45%", "width": "100%"}
        except Exception as e:
            print(f"Error updating pie chart visibility: {e}")
            return {"height": "45%", "width": "100%"}

    @app.callback(
        Output("specialist-table", "data"),
        Input("title-dropdown", "value")
    )
    def update_specialist_table(selected_project):
        try:
            if not selected_project:
                return []
            db = next(database.get_db())
            df = get_executors_data_by_project(db_session=db, title_id=selected_project)
            return df.to_dict("records")
        except Exception as e:
            print(f"Error updating specialist table: {e}")
            return []

    @app.callback(
        Output("specialist-table-container", "style"),
        Input("store-show-table", "data")
    )
    def toggle_table_visibility(store_data):
        return {"height": "45%", "width": "100%", "display": "block" if store_data["show_table"] else "none"}

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
