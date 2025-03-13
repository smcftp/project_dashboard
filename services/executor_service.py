from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Numeric

from database import models

import pandas as pd
import numpy as np

import logging

logging.basicConfig(level=logging.INFO)

def get_executors_data_by_project(db_session: Session, title_id: int):
    try:
        with db_session as db:  # Гарантированное закрытие соединения после выхода из блока
            # Запрос данных
            modeling_query = (
                db.query(
                    models.Executor.executor_name.label("name"),
                    func.round(func.sum(models.ModelingData.total_mass) / 1000000, 2).label("total_mass_modeling")
                )
                .join(models.ModelingData, models.Executor.id == models.ModelingData.executor_id)
                .join(models.Title, models.Title.id == models.ModelingData.title_id)
                .filter(models.Title.id == title_id)
                .group_by(models.Executor.executor_name)
            )

            work_hours_query = (    
                db.query(
                    models.Executor.executor_name.label("name"),
                    func.round(func.sum(models.WorkHoursInWorkSection.hours_worked), 2).label("total_hours"),
                    # func.round(func.sum(models.WorkHoursInTekla.hours_worked) / 3, 2).label("plan_mass")
                )
                # .join(models.WorkHoursInWorkSection, models.Executor.id == models.WorkHoursInWorkSection.executor_id)
                # .join(models.WorksectionTask, models.WorksectionTask.id == models.WorkHoursInWorkSection.task_id)
                # .join(models.Title, models.Title.id == models.WorksectionTask.title_id)
                .join(models.Executor, models.Executor.id == models.WorkHoursInWorkSection.executor_id)
                # .outerjoin(models.WorkHoursInTekla, models.Executor.id == models.WorkHoursInTekla.executor_id)  # ДОБАВЛЕН JOIN
                .filter(models.WorkHoursInWorkSection.title_id == title_id)
                .group_by(models.Executor.executor_name)
            )

            drawing_query = (
                    db.query(
                    models.Executor.executor_name.label("name"),
                    func.round(func.sum(cast(models.DrawingData.number_of_drawings, Numeric)), 0).label("completed_drawings"),
                    func.round(func.sum(cast(models.DrawingData.total_complexity, Numeric)), 0).label("total_complexity_drawing"),
                    func.round(func.sum(cast(models.DrawingData.total_mass, Numeric)), 2).label("total_mass_drawing"),
                )
                .join(models.DrawingData, models.Executor.id == models.DrawingData.executor_id)
                .join(models.Title, models.Title.id == models.DrawingData.title_id)
                .filter(models.Title.id == title_id)
                .group_by(models.Executor.executor_name)
            )

            tekla_hours_query = (
                db.query(
                    models.Executor.executor_name.label("name"),
                    func.round(func.sum(models.WorkHoursInTekla.hours_worked), 0).label("tekla_hours")
                )
                .join(models.WorkHoursInTekla, models.Executor.id == models.WorkHoursInTekla.executor_id)
                .join(models.Title, models.Title.id == models.WorkHoursInTekla.title_id)
                .filter(models.Title.id == title_id)
                .group_by(models.Executor.executor_name)
            )

            # Выполнение запросов
            modeling_result = modeling_query.all()
            work_hours_result = work_hours_query.all()
            drawing_result = drawing_query.all()
            tekla_hours_result = tekla_hours_query.all()
            print("tekla_hours_result = ", tekla_hours_result)

            # Преобразование результатов в DataFrame
            modeling_df = pd.DataFrame(modeling_result, columns=["name", "total_mass_modeling"])
            work_hours_df = pd.DataFrame(work_hours_result, columns=["name", "total_hours"])
            drawing_df = pd.DataFrame(drawing_result, columns=["name", "completed_drawings", "total_complexity_drawing", "total_mass_drawing"])
            tekla_hours_df = pd.DataFrame(tekla_hours_result, columns=["name", "tekla_hours"])
            print("modeling_df = ", modeling_df)
            print("work_hours_df = ", work_hours_df)
            print("drawing_df = ", drawing_df)
            print("tekla_hours_df = ", tekla_hours_df)

            # Объединение данных
            result_df = modeling_df.merge(work_hours_df, on="name", how="outer")
            result_df = result_df.merge(drawing_df, on="name", how="outer")
            result_df = result_df.merge(tekla_hours_df, on="name", how="outer")

            # Обработка NaN значений
            result_df.fillna(0, inplace=True)
            
            result_df["tekla_hours"] = result_df["tekla_hours"].astype(float)
            result_df["total_hours"] = result_df["total_hours"].astype(float)

            result_df["tekla_percentage"] = np.where(
                result_df["total_hours"] != 0,
                (result_df["tekla_hours"] / result_df["total_hours"]) * 100,
                0  # Если total_hours == 0, устанавливаем значение 0
            ).round(1)
            result_df.fillna(0, inplace=True)  # Заполняем NaN после деления


            logging.info("Данные успешно получены и обработаны.")
            return result_df
    except Exception as e:
        logging.error(f"Ошибка при получении данных: {e}")
        return pd.DataFrame(columns=["name", "mass", "total_hours", "plan_mass", "completed_drawings", "tekla_hours", "tekla_percentage"])
