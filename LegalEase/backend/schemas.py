from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=120)
    parties: str = Field(..., min_length=2, max_length=4000)
    terms: str = Field(..., min_length=2, max_length=12000)
    effective_date: str = Field(..., min_length=2, max_length=120)

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "effective_date",
    )
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class DocumentResponse(BaseModel):
    document_type: str
    content: str
    model: str


class ExportRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=120)
    content: str = Field(..., min_length=10, max_length=100000)
    terms: str = Field(default="", max_length=12000)
    effective_date: str = Field(default="", max_length=120)