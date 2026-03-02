"""Model Definition"""

from pydantic import BaseModel, ConfigDict, Field


class MultipartFormDataModel(BaseModel):
    """Model Definition"""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra='forbid')

    content: bytes = Field(..., description='The content of the file.')
    content_type: str = Field(..., description='The Content-Type for the file.')
    filename: str = Field(..., description='The filename for the file.')
    name: str = Field(..., description='The name for the part.')
