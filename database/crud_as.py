from sqlalchemy.ext.asyncio import AsyncSession
from . import models
import unicodedata
from sqlalchemy.future import select  # Добавь импорт

# Функция для очистки имени исполнителя
async def normalize_name(name: str) -> str:
    return unicodedata.normalize("NFKC", name).replace("\xa0", " ").strip()

# Работа с проектами
async def get_project_by_name(db: AsyncSession, project_name: str):
    result = await db.execute(
        models.Project.__table__.select().where(models.Project.project_name == project_name)
    )
    return result.scalar_one_or_none()

async def create_project(db: AsyncSession, project_name: str):
    db_project = models.Project(project_name=project_name)
    db.add(db_project)
    # await db.commit()
    await db.flush()
    # await db.refresh(db_project)
    return db_project

# Работа с заголовками (Titles)
async def get_title_by_name(db: AsyncSession, title_name: str):
    result = await db.execute(
        select(models.Title).where(models.Title.title_name == title_name)
    )
    title = result.scalars().first() 
    
    print(f"[DEBUG] get_title_by_name({title_name}) -> {title}")  
    
    return title  

async def create_title(db: AsyncSession, title_name: str, project_id: int, initial_mass: float = None):
    db_title = models.Title(
        title_name=title_name,
        project_id=project_id,
        initial_mass=initial_mass
    )
    db.add(db_title)
    # await db.commit()
    await db.flush()
    # await db.refresh(db_title)
    return db_title

# Работа с исполнителями
async def get_executor_by_name(db: AsyncSession, executor_name: str):
    normalized_name = await normalize_name(executor_name)
    result = await db.execute(
        select(models.Executor).where(models.Executor.executor_name == normalized_name)  
    )
    executor = result.scalars().first()  
    
    print(f"[DEBUG] get_executor_by_name({executor_name}) -> {executor}")  
    
    return executor 

async def create_executor(db: AsyncSession, executor_number: int, executor_name: str):
    db_executor = models.Executor(executor_number=executor_number, executor_name=executor_name)
    db.add(db_executor)
    # await db.commit()
    await db.flush()
    # await db.refresh(db_executor)

    print(f"[DEBUG] create_executor({executor_name}) -> {db_executor}")  # Лог для отладки

    return db_executor

# Работа с ModelingData
async def create_modeling_data(db: AsyncSession, modeling_data: dict):
    db_modeling_data = models.ModelingData(**modeling_data)
    db.add(db_modeling_data)
    # await db.commit()
    await db.flush()
    # await db.refresh(db_modeling_data)
    return db_modeling_data

# Работа с DrawingData
async def create_drawing_data(db: AsyncSession, drawing_data: dict):
    db_drawing_data = models.DrawingData(**drawing_data)
    db.add(db_drawing_data)
    # await db.commit()
    await db.flush()
    # await db.refresh(db_drawing_data)
    return db_drawing_data

# Работа с WorksectionTask
async def create_worksection_task(db: AsyncSession, task_data: dict):
    db_task = models.WorksectionTask(**task_data)
    db.add(db_task)
    # await db.commit()
    await db.flush()
    # await db.refresh(db_task)
    return db_task

# Работа с WorkHoursInTekla
async def create_work_hours_in_tekla(db: AsyncSession, work_hours: dict):
    db_work_hours = models.WorkHoursInTekla(**work_hours)
    db.add(db_work_hours)
    # await db.commit()
    # await db.refresh(db_work_hours)
    return db_work_hours

# Работа с WorkHoursInWorkSection
async def create_work_hours_in_work_section(db: AsyncSession, work_hours: dict):
    db_work_hours = models.WorkHoursInWorkSection(**work_hours)
    db.add(db_work_hours)
    # await db.commit()
    # await db.refresh(db_work_hours)
    await db.flush()
    return db_work_hours
