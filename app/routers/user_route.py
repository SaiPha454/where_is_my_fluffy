from fastapi import APIRouter

router = APIRouter(tags=["users"])

@router.get("/users")
async def get_users():
    return "user endpoint"