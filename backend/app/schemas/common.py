from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None

class ApiResponse(BaseModel, Generic[DataT]):
    success: bool = True
    data: Optional[DataT] = None
    error: Optional[ErrorDetail] = None
    meta: Optional[dict] = None
