from sqlalchemy.orm import Session
from . import models

# Работа с проектами
def get_project_by_name(db: Session, project_name: str):
    return db.query(models.Project).filter(models.Project.project_name == project_name).first()

def create_project(db: Session, project_name: str):
    db_project = models.Project(project_name=project_name)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# Работа с заголовками (Titles)
def get_title_by_name(db: Session, title_name: str):
    return db.query(models.Title).filter(models.Title.title_name == title_name).first()

def create_title(db: Session, title_name: str, project_id: int):
    db_title = models.Title(title_name=title_name, project_id=project_id)
    db.add(db_title)
    db.commit()
    db.refresh(db_title)
    return db_title

# Работа с главами (TitleChapter)
def create_title_chapter(db: Session, chapter_name: str, title_id: int):
    db_chapter = models.TitleChapter(chapter_name=chapter_name, title_id=title_id)
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter

# Работа с исполнителями
def get_executor_by_number(db: Session, executor_number: int):
    return db.query(models.Executor).filter(models.Executor.executor_number == executor_number).first()

def create_executor(db: Session, executor_number: int, executor_name: str):
    db_executor = models.Executor(executor_number=executor_number, executor_name=executor_name)
    db.add(db_executor)
    db.commit()
    db.refresh(db_executor)
    return db_executor

# Работа с ModelingData
def create_modeling_data(db: Session, modeling_data: dict):
    db_modeling_data = models.ModelingData(**modeling_data)
    db.add(db_modeling_data)
    db.commit()
    db.refresh(db_modeling_data)
    return db_modeling_data

# Работа с DrawingData
def create_drawing_data(db: Session, drawing_data: dict):
    db_drawing_data = models.DrawingData(**drawing_data)
    db.add(db_drawing_data)
    db.commit()
    db.refresh(db_drawing_data)
    return db_drawing_data

# Работа с WorksectionTask
def create_worksection_task(db: Session, task_data: dict):
    db_task = models.WorksectionTask(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Работа с WorkHoursInTekla
def create_work_hours_in_tekla(db: Session, work_hours: dict):
    db_work_hours = models.WorkHoursInTekla(**work_hours)
    db.add(db_work_hours)
    db.commit()
    db.refresh(db_work_hours)
    return db_work_hours

# Работа с WorkHoursInWorkSection
def create_work_hours_in_work_section(db: Session, work_hours: dict):
    db_work_hours = models.WorkHoursInWorkSection(**work_hours)
    db.add(db_work_hours)
    db.commit()
    db.refresh(db_work_hours)
    return db_work_hours
