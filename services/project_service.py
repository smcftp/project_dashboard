from sqlalchemy.orm import Session
from database import models
from sqlalchemy import func
import pandas as pd


# Получение списка проектов из базы данных
def get_project_list(db: Session):
    projects = db.query(models.Project).all()
    return [{"label": project.project_name, "value": project.id} for project in projects]

# Получение списка заголовков по проекту
def get_titles_by_project(db: Session, project_id: int):
    titles = db.query(models.Title).filter(models.Title.project_id == project_id).all()
    return [{"label": title.title_name, "value": title.id} for title in titles]

# Получение списка глав по заголовку
def get_chapters_by_title(db: Session, title_id: int):
    chapters = db.query(models.TitleChapter).filter(models.TitleChapter.title_id == title_id).all()
    return [{"label": chapter.chapter_name, "value": chapter.id} for chapter in chapters]

# Получение задач по главе
def get_tasks_by_chapter(db: Session, chapter_id: int):
    tasks = db.query(models.WorksectionTask).filter(models.WorksectionTask.chapter_id == chapter_id).all()
    return [{"label": task.task_name, "value": task.id} for task in tasks]

# Получение всех задач по проекту (связано через заголовки и главы)
def get_tasks_by_project(db: Session, project_id: int):
    tasks = db.query(models.WorksectionTask).join(models.Title).filter(models.Title.project_id == project_id).all()
    return [{"label": task.task_name, "value": task.id} for task in tasks]

# Получение рабочего времени для задачи
def get_work_hours_for_task(db: Session, task_id: int):
    work_hours = db.query(models.WorkHoursInWorkSection).filter(models.WorkHoursInWorkSection.task_id == task_id).all()
    return [{"executor_id": work_hour.executor_id, "hours_worked": work_hour.hours_worked} for work_hour in work_hours]

# Получение данных моделирования для задачи
def get_modeling_data_for_task(db: Session, task_id: int):
    modeling_data = db.query(models.ModelingData).filter(models.ModelingData.title_id == task_id).all()
    return [{"executor_id": data.executor_id, "total_mass": data.total_mass, "total_complexity": data.total_complexity} for data in modeling_data]

# Получение данных чертежей для задачи
def get_drawing_data_for_task(db: Session, task_id: int):
    drawing_data = db.query(models.DrawingData).filter(models.DrawingData.title_id == task_id).all()
    return [{"executor_id": data.executor_id, "number_of_drawings": data.number_of_drawings} for data in drawing_data]

def get_time_by_chapter_for_title(db: Session, title_id: int):
    try:
        query = (
            db.query(
                models.TitleChapter.chapter_name.label("chapter_name"),
                func.sum(models.WorksectionTask.time).label("total_time")
            )
            .join(models.WorksectionTask, models.WorksectionTask.chapter_id == models.TitleChapter.id)
            .filter(models.WorksectionTask.title_id == title_id)
            .group_by(models.TitleChapter.chapter_name)
        )

        result = query.all()

        if not result:
            print(f"⚠️ Нет данных для title_id: {title_id}")
            return None

        df = pd.DataFrame(result, columns=["chapter_name", "total_time"])
        df["total_time"] = df["total_time"].fillna(0).astype(float)

        total_time = df["total_time"].sum()
        df["percentage"] = (df["total_time"] / total_time) * 100 if total_time > 0 else 0

        return df

    except Exception as e:
        print(f"❌ Ошибка при получении данных: {e}")
        return None

    finally:
        db.close()  # Закрываем соединение вручную

