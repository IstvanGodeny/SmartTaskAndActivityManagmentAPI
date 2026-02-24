from fastapi import APIRouter

from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.tasks import router as tasks_router

router = APIRouter()

# Health check for the API. Is the server on? Is the API working? If so respond: status: ok
@router.get("/health")
def health():
    return {"status": "ok"}

# Operations of Users
router.include_router(users_router)
# Login
router.include_router(auth_router)
# Operations of tasks
router.include_router(tasks_router)