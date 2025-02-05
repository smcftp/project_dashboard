from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from database import models

import pandas as pd

import logging

def get_drawing_data_for_project(db: Session, title_id: int):
    """
    Получает данные по чертежам для указанного проекта и возвращает их в виде DataFrame.
    
    :param db: Сессия базы данных SQLAlchemy
    :param title_id: ID проекта (title_id)
    :return: DataFrame с колонками [Дата, Всего чертежей]
    """
    try:
        drawing_query = (
            db.query(
                models.DrawingData.date,
                func.sum(models.DrawingData.number_of_drawings).label("total_drawings")
            )
            .join(models.Title, models.DrawingData.title_id == models.Title.id)
            .filter(models.DrawingData.title_id == title_id)
            .group_by(models.DrawingData.date)
            .order_by(models.DrawingData.date)
        )
        drawing_result = drawing_query.all()

        drawing_df = pd.DataFrame(drawing_result, columns=["Дата", "Всего чертежей"])
        drawing_df["Дата"] = pd.to_datetime(drawing_df["Дата"], errors="coerce")

        if drawing_df.empty:
            print("❌ DataFrame для линейных пуст!")

        return drawing_df

    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return pd.DataFrame(columns=["Дата", "Всего чертежей"])  # Возвращаем пустой DataFrame
    finally:
        db.close()  # Закрываем соединение, если оно было открыто


def get_data_for_project(db: Session, title_id: int):
    """
    Получает данные по смоделированым конструкциям для указанного проекта и возвращает их в виде DataFrame.
    Получает данные по часам проведеным специалистов в Tekla для указанного проекта и возвращает их в виде DataFrame.
    
    :param db: Сессия базы данных SQLAlchemy
    :param title_id: ID проекта (title_id)
    :return: DataFrame с колонками [Дата, Масса, Сложность, Общие часы]
    """
    if not isinstance(title_id, int) or title_id <= 0:
        raise ValueError("Некорректный `title_id`, должен быть положительным числом.")

    try:
        # Запрос для моделирования
        modeling_query = (
            db.query(
                models.ModelingData.date,
                (func.sum(models.ModelingData.total_mass) / 100000000).label("total_mass"),
                (func.sum(models.ModelingData.total_complexity) / func.count(models.ModelingData.total_complexity)).label("avg_complexity")
            )
            .join(models.Title, models.ModelingData.title_id == models.Title.id)
            .filter(models.ModelingData.title_id == title_id)  # Исправлена ошибка с `DrawingData`
            .group_by(models.ModelingData.date)
            .order_by(models.ModelingData.date)
        )
        modeling_result = modeling_query.all()

        # Запрос по рабочим часам
        work_hours_query = (
            db.query(
                models.WorkHoursInTekla.date,
                func.sum(models.WorkHoursInTekla.hours_worked).label("total_hours")
            )
            .filter(models.WorkHoursInTekla.title_id == title_id)
            .group_by(models.WorkHoursInTekla.date)
        )
        work_hours_result = work_hours_query.all()

        # Создание DataFrame
        modeling_df = pd.DataFrame(modeling_result, columns=["Дата", "Масса", "Сложность"])
        work_hours_df = pd.DataFrame(work_hours_result, columns=["Дата", "Общие часы"])

        # Преобразование даты
        modeling_df["Дата"] = pd.to_datetime(modeling_df["Дата"], errors="coerce")
        work_hours_df["Дата"] = pd.to_datetime(work_hours_df["Дата"], errors="coerce")

        # Объединение
        result_df = pd.merge(modeling_df, work_hours_df, on="Дата", how="left").fillna(0)

        # Рассчёт плановой массы
        result_df["Плановая масса"] = result_df["Общие часы"] / 3

        if result_df.empty:
            print("⚠️ DataFrame пуст!")

        return result_df

    except SQLAlchemyError as e:
        print(f"❌ Ошибка БД: {e}")
        db.rollback()  # Откат транзакции в случае ошибки
        return None
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        return None
    finally:
        db.close()  # Закрытие соединения
