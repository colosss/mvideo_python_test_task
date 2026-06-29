from fastapi import APIRouter
from src.interfaces.api.constants import SERVICE_NAME

router=APIRouter(tags=["Health"])

@router.get("/health")
async def health()->dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}