"""Model Definition"""

from typing import Generic, TypeVar

from core.model.response.response_model import ResponseModel

T = TypeVar('T')


class PaginatedResponseModel(ResponseModel[list[T]], Generic[T]):
    """Paginated Collection Response Model"""

    count: int
    data: list[T]
    next: str | None = None
    prev: str | None = None
    status: str | None = None
    total_count: int
