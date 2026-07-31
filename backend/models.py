"""数据模型定义"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CourseCreate(BaseModel):
    name: str
    topic: str
    major: str
    student_level: str = "高职本科（应用型本科）"
    class_hours: int = 8
    group_size: int = 4
    project_type: str
    project_scenario: Optional[str] = None
    learning_objectives: Optional[str] = None


class CourseResponse(CourseCreate):
    id: int
    created_at: Optional[str] = None


class GenerateRequest(BaseModel):
    course: CourseCreate
    resource_types: list[str]
    model: str = "deepseek-v4-flash"
    temperature: float = 0.7
    # 访客必须提供自己的 API Key（本系统不内置任何 Key）
    api_key: str
    base_url: Optional[str] = None


class ResourceResponse(BaseModel):
    id: int
    course_id: int
    resource_type: str
    content: str
    model_used: Optional[str] = None
    temperature: Optional[float] = None
    created_at: Optional[str] = None


class HistoryResponse(BaseModel):
    id: int
    course_id: int
    resource_types: str
    status: str
    error_message: Optional[str] = None
    created_at: Optional[str] = None
