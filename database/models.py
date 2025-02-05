# models.py
from sqlalchemy import Column, Integer, Text, Date, Numeric, ForeignKey, Time
from sqlalchemy.orm import relationship
from .db import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    project_name = Column(Text, unique=True, nullable=False)
    
    titles = relationship("Title", back_populates="project")


class Title(Base):
    __tablename__ = "titles"
    id = Column(Integer, primary_key=True)
    title_name = Column(Text, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    initial_mass = Column(Numeric, nullable=True)  # Новое поле для хранения тоннажа

    project = relationship("Project", back_populates="titles")
    chapters = relationship("TitleChapter", back_populates="title")
    modeling_data = relationship("ModelingData", back_populates="title")
    drawing_data = relationship("DrawingData", back_populates="title")
    worksection_tasks = relationship("WorksectionTask", back_populates="title")
    work_hours_in_work_section = relationship("WorkHoursInWorkSection", back_populates="title")


class TitleChapter(Base):
    __tablename__ = "title_chapters"
    id = Column(Integer, primary_key=True)
    chapter_name = Column(Text, nullable=False)
    title_id = Column(Integer, ForeignKey("titles.id"))
    
    title = relationship("Title", back_populates="chapters")
    worksection_tasks = relationship("WorksectionTask", back_populates="chapter")


class WorksectionTask(Base):
    __tablename__ = "worksection_tasks"
    id = Column(Integer, primary_key=True)
    task_name = Column(Text, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Numeric, nullable=False)
    money = Column(Numeric, nullable=False)
    user_id = Column(Integer, ForeignKey("executors.id"))
    title_id = Column(Integer, ForeignKey("titles.id"))
    chapter_id = Column(Integer, ForeignKey("title_chapters.id"))
    
    executor = relationship("Executor", back_populates="worksection_tasks")
    title = relationship("Title", back_populates="worksection_tasks")
    chapter = relationship("TitleChapter", back_populates="worksection_tasks")
    work_hours = relationship("WorkHoursInWorkSection", back_populates="task")


class Executor(Base):
    __tablename__ = "executors"
    id = Column(Integer, primary_key=True)
    executor_number = Column(Integer, unique=True)
    executor_name = Column(Text)
    
    modeling_data = relationship("ModelingData", back_populates="executor")
    drawing_data = relationship("DrawingData", back_populates="executor")
    work_hours = relationship("WorkHoursInTekla", back_populates="executor")
    worksection_tasks = relationship("WorksectionTask", back_populates="executor")
    work_hours_in_work_section = relationship("WorkHoursInWorkSection", back_populates="executor")


class WorkHoursInTekla(Base):
    __tablename__ = "work_hours_in_tekla"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    executor_id = Column(Integer, ForeignKey("executors.id"))
    title_id = Column(Integer, ForeignKey("titles.id"))
    hours_worked = Column(Numeric)
    
    executor = relationship("Executor", back_populates="work_hours")
    title = relationship("Title")


class ModelingData(Base):
    __tablename__ = "modeling_data"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    executor_id = Column(Integer, ForeignKey("executors.id"))
    title_id = Column(Integer, ForeignKey("titles.id"))
    total_mass = Column(Numeric)
    total_complexity = Column(Numeric)
    number_of_records = Column(Integer)
    
    executor = relationship("Executor", back_populates="modeling_data")
    title = relationship("Title", back_populates="modeling_data")


class DrawingData(Base):
    __tablename__ = "drawing_data"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    executor_id = Column(Integer, ForeignKey("executors.id"))
    title_id = Column(Integer, ForeignKey("titles.id"))
    number_of_drawings = Column(Integer, nullable=False)
    
    executor = relationship("Executor", back_populates="drawing_data")
    title = relationship("Title", back_populates="drawing_data")


class WorkHoursInWorkSection(Base):
    __tablename__ = "work_hours_in_work_section"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    task_id = Column(Integer, ForeignKey("worksection_tasks.id"))
    title_id = Column(Integer, ForeignKey("titles.id"))
    executor_id = Column(Integer, ForeignKey("executors.id"))
    hours_worked = Column(Numeric)
    
    task = relationship("WorksectionTask", back_populates="work_hours")
    title = relationship("Title", back_populates="work_hours_in_work_section")
    executor = relationship("Executor", back_populates="work_hours_in_work_section")

