"""FastAPI 主应用"""
import os
import json
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List

from database import init_db, get_db
from models import (
    CourseCreate, CourseResponse, GenerateRequest,
    ResourceResponse, HistoryResponse
)
from ai_service import generate_resource

# 全局变量存储生成进度
generation_progress = {
    "is_running": False,
    "current": 0,
    "total": 0,
    "current_resource": "",
    "results": {}
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    init_db()
    yield


app = FastAPI(
    title="PBL 教学资源生成器",
    description="面向高职本科数据科学类专业的AI辅助教学设计工具",
    version="2.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件目录
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")


# ==================== API 路由 ====================

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "PBL 教学资源生成器运行正常"}


@app.get("/api/providers")
async def list_providers():
    """获取大模型服务商预设列表"""
    from ai_service import PROVIDER_PRESETS
    return PROVIDER_PRESETS


@app.post("/api/courses", response_model=CourseResponse)
async def create_course(course: CourseCreate):
    """创建课程"""
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO courses (name, topic, major, student_level, class_hours, group_size, project_type, project_scenario, learning_objectives)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            course.name, course.topic, course.major, course.student_level,
            course.class_hours, course.group_size, course.project_type,
            course.project_scenario, course.learning_objectives
        ))
        db.commit()
        course_id = cursor.lastrowid

        return CourseResponse(
            id=course_id,
            **course.model_dump()
        )
    finally:
        db.close()


@app.get("/api/courses", response_model=List[CourseResponse])
async def list_courses():
    """获取课程列表"""
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM courses ORDER BY created_at DESC")
        courses = cursor.fetchall()
        return [dict(c) for c in courses]
    finally:
        db.close()


@app.get("/api/courses/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int):
    """获取单个课程"""
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        course = cursor.fetchone()
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        return dict(course)
    finally:
        db.close()


@app.delete("/api/courses/{course_id}")
async def delete_course(course_id: int):
    """删除课程"""
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="课程不存在")
        return {"message": "课程已删除"}
    finally:
        db.close()


@app.post("/api/generate")
async def generate_resources(request: GenerateRequest):
    """生成教学资源"""
    global generation_progress

    # 所有访客必须提供自己的 API Key
    if not request.api_key or not request.api_key.strip():
        raise HTTPException(status_code=400, detail="请填写您自己的 API Key")

    # 先保存课程
    db = get_db()
    try:
        cursor = db.cursor()
        course_data = request.course.model_dump()

        cursor.execute("""
            INSERT INTO courses (name, topic, major, student_level, class_hours, group_size, project_type, project_scenario, learning_objectives)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            course_data['name'], course_data['topic'], course_data['major'],
            course_data['student_level'], course_data['class_hours'],
            course_data['group_size'], course_data['project_type'],
            course_data.get('project_scenario'), course_data.get('learning_objectives')
        ))
        db.commit()
        course_id = cursor.lastrowid
    finally:
        db.close()

    # 初始化进度
    generation_progress = {
        "is_running": True,
        "current": 0,
        "total": len(request.resource_types),
        "current_resource": "",
        "results": {},
        "course_id": course_id
    }

    # 逐个生成资源
    for resource_type in request.resource_types:
        generation_progress["current_resource"] = resource_type

        try:
            content = generate_resource(
                course_data,
                resource_type,
                request.model,
                request.temperature,
                api_key=request.api_key,
                base_url=request.base_url
            )

            # 保存到数据库
            db = get_db()
            try:
                cursor = db.cursor()
                cursor.execute("""
                    INSERT INTO resources (course_id, resource_type, content, model_used, temperature)
                    VALUES (?, ?, ?, ?, ?)
                """, (course_id, resource_type, content, request.model, request.temperature))
                db.commit()
                resource_id = cursor.lastrowid
            finally:
                db.close()

            generation_progress["results"][resource_type] = {
                "id": resource_id,
                "content": content
            }

        except Exception as e:
            generation_progress["results"][resource_type] = {
                "error": str(e)
            }

        generation_progress["current"] += 1

    # 记录历史
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO generation_history (course_id, resource_types, status)
            VALUES (?, ?, ?)
        """, (course_id, json.dumps(request.resource_types), "success"))
        db.commit()
    finally:
        db.close()

    generation_progress["is_running"] = False

    return {
        "course_id": course_id,
        "results": generation_progress["results"]
    }


@app.get("/api/generate/progress")
async def get_generation_progress():
    """获取生成进度"""
    return generation_progress


@app.get("/api/courses/{course_id}/resources", response_model=List[ResourceResponse])
async def list_resources(course_id: int):
    """获取课程的所有资源"""
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM resources WHERE course_id = ? ORDER BY created_at", (course_id,))
        resources = cursor.fetchall()
        return [dict(r) for r in resources]
    finally:
        db.close()


@app.get("/api/history", response_model=List[HistoryResponse])
async def list_history():
    """获取生成历史"""
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM generation_history ORDER BY created_at DESC LIMIT 50")
        history = cursor.fetchall()
        return [dict(h) for h in history]
    finally:
        db.close()


# ==================== 静态文件服务 ====================

@app.get("/")
async def serve_index():
    """提供首页"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/style.css")
async def serve_css():
    return FileResponse(os.path.join(STATIC_DIR, "style.css"), media_type="text/css")


@app.get("/app.js")
async def serve_js():
    return FileResponse(os.path.join(STATIC_DIR, "app.js"), media_type="application/javascript")


# 挂载静态文件目录
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
