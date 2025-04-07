from fastapi import APIRouter
from app.routes import user, courses, enrollments, llm, faculty, chat, assignments, quiz, swagger, auth, transcription

api_router = APIRouter()

api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
api_router.include_router(faculty.router, prefix="/faculty", tags=["faculty"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
api_router.include_router(llm.router, prefix="/llm", tags=["llm"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(swagger.router, prefix="/swagger", tags=["swagger"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(transcription.router, prefix="/transcription", tags=["transcription"]) 