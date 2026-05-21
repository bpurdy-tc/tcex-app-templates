"""Model Definition"""

from pydantic import BaseModel


class PaginatorResponseModel(BaseModel):
    """Model Definition"""

    count: int | None = None
    data: list[dict] | None = None
    next: str | None = None
    previous: str | None = None
    total_count: int | None = None
