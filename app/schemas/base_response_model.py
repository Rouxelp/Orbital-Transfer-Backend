from pydantic import BaseModel, Field

class BaseResponseModel(BaseModel):
    page: int = Field(
        ...,
        ge=1,
        description="The current page number, starting from 1."
    )
    page_size: int = Field(
        50,
        ge=1,
        le=100,
        description="The number of items per page, must be between 1 and 100."
    )
