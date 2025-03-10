from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, case
from decimal import Decimal

from database import models

import pandas as pd

import logging

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Numeric
from decimal import Decimal
# from . import models

def get_drawing_data_for_project(db: Session, title_id: int):
    """
    Получает данные по чертежам для указанного проекта и возвращает их в виде DataFrame.

    :param db: Сессия базы данных SQLAlchemy
    :param title_id: ID проекта (title_id)
    :return: DataFrame с колонками [Дата, Всего чертежей, Сложность, Масса, Общие часы, Плановая масса]
    """
    try:
        # 🔍 Проверка title_id
        if title_id is None:
            print("❌ Ошибка: `title_id` = None. Проверьте источник данных!")
            return pd.DataFrame(columns=["Дата", "Всего чертежей"])

        # print(f"🔍 Проверка title_id: {title_id}")

        # 🔎 Запрос данных о чертежах
        drawing_query = (
            db.query(
                models.DrawingData.date,
                func.round(func.sum(cast(models.DrawingData.number_of_drawings, Numeric)), 0).label("total_drawings"),
                func.sum(cast(models.DrawingData.total_complexity, Numeric)).label("total_complexity"),
                func.round(func.sum(cast(models.DrawingData.total_mass, Numeric)), 2).label("total_mass"),
            )
            .filter(models.DrawingData.title_id == title_id)
            .filter(models.DrawingData.date.isnot(None))
            .group_by(models.DrawingData.date)
            .order_by(models.DrawingData.date)
        )
        drawing_result = drawing_query.all()
        # print("drawing_result", drawing_result)

        # 🔎 Запрос данных о рабочих часах
        subquery = (
            db.query(
                models.WorkHoursInTekla.date,
                models.WorkHoursInTekla.executor_id,
                func.coalesce(
                    func.max(
                        case(
                            (models.WorkHoursInTekla.hours_worked.is_(None), 0),  # NULL → 0
                            (models.WorkHoursInTekla.hours_worked == float("NaN"), 0),  # NaN → 0
                            (models.WorkHoursInTekla.hours_worked == Decimal("NaN"), 0),  # Decimal(NaN) → 0
                            else_=models.WorkHoursInTekla.hours_worked,  # Оставляем нормальные значения
                        )
                    ),
                    0,  # Если всё же попал NULL
                ).label("unique_hours")
            )
            .filter(models.WorkHoursInTekla.title_id == title_id)
            .filter(models.WorkHoursInTekla.date.isnot(None))
            .group_by(models.WorkHoursInTekla.date, models.WorkHoursInTekla.executor_id)  # Группируем по дате и исполнителю
            .subquery()
        )
 
        result = db.query(subquery).all()
        # print(f"📊 Данные в subquery: {result}")

        # Теперь агрегируем по дням
        work_hours_query = (
            db.query(
                subquery.c.date,
                func.coalesce(func.sum(subquery.c.unique_hours), 0).label("total_hours")
            )
            .group_by(subquery.c.date)
            .order_by(subquery.c.date)
        )

        work_hours_result = work_hours_query.all()

        # 📊 Отладка: проверяем, что запросы вернули данные
        # print(f"📝 Данные по чертежам: {drawing_result}")
        # print(f"⏳ Данные по рабочим часам: {work_hours_result}")

        # 📌 Создание DataFrame из результатов
        drawing_df = pd.DataFrame(drawing_result, columns=["Дата", "Всего чертежей", "Сложность", "Масса"])
        work_hours_df = pd.DataFrame(work_hours_result, columns=["Дата", "Общие часы"])

        # 🛠 Обработка пустых DataFrame
        if drawing_df.empty:
            print("⚠️ DataFrame drawing_df пуст! Нет данных о чертежах.")
        if work_hours_df.empty:
            print("⚠️ DataFrame work_hours_df пуст! Нет данных о рабочих часах.")

        # 🗓 Преобразование колонок с датами
        drawing_df["Дата"] = pd.to_datetime(drawing_df["Дата"], errors="coerce")
        work_hours_df["Дата"] = pd.to_datetime(work_hours_df["Дата"], errors="coerce")
        work_hours_df["Общие часы"] = work_hours_df["Общие часы"].apply(lambda x: 0 if isinstance(x, Decimal) and x.is_nan() else float(x))

        # 🔄 Объединение данных по дате (outer join для сохранения всех записей)
        final_df = pd.merge(drawing_df, work_hours_df, on="Дата", how="outer").fillna(0)

        # 📊 Рассчёт плановой массы (Пример: 1.6 - коэффициент, если есть другие данные, можно изменить)
        final_df["Плановая масса"] = final_df["Общие часы"] / 1.6

        # 🛠 Финальная проверка: если DataFrame пуст, выводим сообщение
        if final_df.empty:
            print("❌ Итоговый DataFrame пуст! Возможно, нет данных в таблицах.")

        # print(final_df)  # Отладочный вывод
        
        return final_df

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
                (func.sum(models.ModelingData.total_mass)).label("total_mass"),
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
        result_df["Плановая масса"] = result_df["Общие часы"] / 1.4

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
        
        
def get_completed_mass_for_project_mod(db: Session, title_id: int):
    """
    Получает суммарную выполненную массу для указанного титула.
    
    :param db: Сессия базы данных SQLAlchemy
    :param title_id: ID титула
    :return: Суммарная масса
    """
    if not isinstance(title_id, int) or title_id <= 0:
        raise ValueError("Некорректный `title_id`, должен быть положительным числом.")

    try:
        # 🔹 Запрос суммарной массы из `ModelingData`
        completed_mass_query = (
            db.query(
                func.coalesce(func.sum(models.ModelingData.total_mass), 0).label("completed_mass")
            )
            .join(models.Title, models.ModelingData.title_id == models.Title.id)
            .filter(models.ModelingData.title_id == title_id)
        )
        completed_mass_result = completed_mass_query.one_or_none()
        # print("completed_mass_result = ", completed_mass_result)

        # 🔹 Запрос плановой массы из `Title`
        title_plan_mass_query = (
            db.query(func.coalesce(models.Title.initial_mass, 0).label("initial_mass"))
            .filter(models.Title.id == title_id)
        )
        title_plan_mass_result = title_plan_mass_query.one_or_none()

        # 📌 Извлекаем значения
        completed_mass = completed_mass_result.completed_mass if completed_mass_result else 0
        initial_mass = title_plan_mass_result.initial_mass if title_plan_mass_result else 0

        # 🔍 Проверка корректности `completed_mass`
        if completed_mass <= 0:
            print(f"⚠️ Внимание: `completed_mass` для титула {title_id} некорректен ({completed_mass})")
        
        # 🔍 Проверка корректности `initial_mass`
        if initial_mass <= 0:
            print(f"⚠️ Внимание: `initial_mass` для титула {title_id} некорректен ({initial_mass})")

        # 📌 Если обе массы некорректны, возвращаем `0`
        if completed_mass <= 0 and initial_mass <= 0:
            return 0, 0

        return completed_mass, initial_mass  # Возвращаем оба значения

    except SQLAlchemyError as e:
        print(f"❌ Ошибка БД: {e}")
        db.rollback()
        return None
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        return None
    finally:
        db.close()
        
        
def get_completed_mass_for_project_dr(db: Session, title_id: int):
    """
    Получает суммарную выполненную массу для указанного титула.
    
    :param db: Сессия базы данных SQLAlchemy
    :param title_id: ID титула
    :return: Суммарная масса
    """
    if not isinstance(title_id, int) or title_id <= 0:
        raise ValueError("Некорректный `title_id`, должен быть положительным числом.")

    try:
        # 🔹 Запрос суммарной массы из `DrawingData`
        completed_mass_query = (
            db.query(
                func.coalesce(func.sum(models.DrawingData.total_mass), 0).label("completed_mass")
            )
            .join(models.Title, models.DrawingData.title_id == models.Title.id)
            .filter(models.DrawingData.title_id == title_id)
        )
        completed_mass_result = completed_mass_query.one_or_none()
        print("completed_mass_result = ", completed_mass_result)

        # 🔹 Запрос плановой массы из `Title`
        title_plan_mass_query = (
            db.query(func.coalesce(models.Title.initial_mass, 0).label("initial_mass"))
            .filter(models.Title.id == title_id)
        )
        title_plan_mass_result = title_plan_mass_query.one_or_none()

        # 📌 Извлекаем значения
        completed_mass = completed_mass_result.completed_mass if completed_mass_result else 0
        initial_mass = title_plan_mass_result.initial_mass if title_plan_mass_result else 0

        # 🔍 Проверка корректности `completed_mass`
        if completed_mass <= 0:
            print(f"⚠️ Внимание: `completed_mass` для титула {title_id} некорректен ({completed_mass})")
        
        # 🔍 Проверка корректности `initial_mass`
        if initial_mass <= 0:
            print(f"⚠️ Внимание: `initial_mass` для титула {title_id} некорректен ({initial_mass})")

        # 📌 Если обе массы некорректны, возвращаем `0`
        if completed_mass <= 0 and initial_mass <= 0:
            return 0, 0

        return completed_mass, initial_mass  # Возвращаем оба значения

    except SQLAlchemyError as e:
        print(f"❌ Ошибка БД: {e}")
        db.rollback()
        return None
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        return None
    finally:
        db.close()
