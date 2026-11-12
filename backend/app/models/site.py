from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4


class Site(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    id: UUID = Field(default_factory=uuid4)

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    location: str = Field(
        min_length=2,
        max_length=150,
    )

    industry: str = Field(
        min_length=2,
        max_length=100,
    )

    workforce_size: int = Field(
        gt=0,
        le=100000,
    )

    active: bool = True