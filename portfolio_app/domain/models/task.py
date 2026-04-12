"""domain/models/task.py — Proje task entity."""

from dataclasses import dataclass
from typing import Optional

from domain.enums.task_type import TaskType, TaskStatus


@dataclass
class Task:
    id: Optional[int]
    project_id: int
    type: TaskType = TaskType.GOREV
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.BEKLIYOR
    display_order: int = 0
    created_at: str = ""
