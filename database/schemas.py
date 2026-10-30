from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BatchCreate(BaseModel):
    batch_code: str
    product_name: str
    temperature: float
    humidity: float
    remaining_shelf_life: float


class BatchUpdate(BaseModel):
    product_name: str
    temperature: float
    humidity: float
    remaining_shelf_life: float


class BatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_code: str
    product_name: str
    status: str
    temperature: float
    humidity: float
    remaining_shelf_life: float
    created_at: datetime