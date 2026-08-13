from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Standardized API Success Response Envelope.
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    success: bool = Field(default=True, example=True)
    message: str = Field(default="Operation completed successfully", example="Success")
    data: Optional[T] = Field(default=None)


class APIErrorResponse(BaseModel):
    """
    Standardized API Error Response Envelope.
    """
    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(default=False, example=False)
    message: str = Field(default="An error occurred", example="Resource not found")
    errors: List[Any] = Field(default_factory=list, example=["Invalid ID parameter"])
