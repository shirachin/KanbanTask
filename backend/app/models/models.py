from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_month = Column(String, nullable=True)  # YYYY-MM形式
    end_month = Column(String, nullable=True)  # YYYY-MM形式
    assignee = Column(String, nullable=True)  # JSON配列として保存（カンマ区切りまたはJSON）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    statuses = relationship(
        "Status", back_populates="project"
    )  # cascadeを削除（共通ステータスは削除しない）


class Status(Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    order = Column(Integer, default=0)
    color = Column(String, default="#667eea")
    project_id = Column(
        Integer, ForeignKey("projects.id"), nullable=True
    )  # 共通ステータスの場合はNULL
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="statuses")
    tasks = relationship("Task", back_populates="status_obj")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="not_started")
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assignee = Column(String, nullable=True)  # 担当者（個人タスク用）
    order = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="tasks")
    status_obj = relationship("Status", back_populates="tasks")
    todos = relationship(
        "Todo", back_populates="task", cascade="all, delete-orphan", order_by="Todo.order"
    )


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    scheduled_date = Column(DateTime(timezone=True), nullable=True)  # 実行予定日
    completed_date = Column(DateTime(timezone=True), nullable=True)  # 実行完了日
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    task = relationship("Task", back_populates="todos")
