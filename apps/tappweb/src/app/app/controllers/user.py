from fastapi import APIRouter, Depends, status

from app.app.schemas import UserCreateRequest
from app.app.services.service import Service


router = APIRouter()


@router.post(
    "/", response_model=UserCreateRequest, status_code=status.HTTP_200_OK, description="Create user", name="Create user"
)
async def create_user(request: UserCreateRequest, service: Service = Depends(Service)):
    return await service.create_user(**request.dict())
