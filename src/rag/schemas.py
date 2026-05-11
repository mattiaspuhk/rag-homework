from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_serializer,
    model_validator,
)

Confidence = Literal["high", "medium", "low"]
QuestionStatus = Literal["answered", "not_found"]


class Source(BaseModel):
    """A single piece of grounding evidence pulled from the source PDF."""

    model_config = ConfigDict(extra="forbid")

    page: int | None = Field(
        default=None,
        ge=1,
        description="1-indexed page number; null if the loader could not attribute one.",
    )
    quote: str = Field(min_length=1)


class Summary(BaseModel):
    """A short, grounded summary of a single company's report."""

    model_config = ConfigDict(extra="forbid")

    answer: str = Field(min_length=1)
    sources: list[Source] = Field(default_factory=list)


class Document(BaseModel):
    """Identifying metadata for a single source PDF."""

    model_config = ConfigDict(extra="forbid")

    file_name: str = Field(min_length=1)
    report_year: str = Field(min_length=4)
    source_url: HttpUrl


class QuestionResult(BaseModel):
    """The result for a single predefined question against one company's report."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    status: QuestionStatus
    answer: str | None = None
    confidence: Confidence
    sources: list[Source] = Field(default_factory=list)
    missing_information: str | None = None

    @model_validator(mode="after")
    def _enforce_status_invariants(self) -> "QuestionResult":
        # The spec ties answer/sources/missing_information to status:
        # answered  -> answer is non-empty, at least one source, no missing_information
        # not_found -> answer is null, sources empty, missing_information explains the gap
        if self.status == "answered":
            if not self.answer or not self.answer.strip():
                raise ValueError("answered questions must have a non-empty answer")
            if not self.sources:
                raise ValueError("answered questions must include at least one source")
            if self.missing_information is not None:
                raise ValueError("missing_information must be null when status is 'answered'")
        else:
            if self.answer is not None:
                raise ValueError("not_found questions must have answer == null")
            if self.sources:
                raise ValueError("not_found questions must have an empty sources list")
            if not self.missing_information or not self.missing_information.strip():
                raise ValueError("not_found questions must include missing_information")
        return self


class ModelInfo(BaseModel):
    """Identifies which provider and model produced this artifact."""

    model_config = ConfigDict(extra="forbid")

    provider: str = Field(min_length=1)
    name: str = Field(min_length=1)


class CompanyResult(BaseModel):
    """All generated outputs for a single company."""

    model_config = ConfigDict(extra="forbid")

    company_name: str = Field(min_length=1)
    document: Document
    summary: Summary
    questions: list[QuestionResult]


class Results(BaseModel):
    """Root of the generated JSON artifact written to data/output/results.json."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    generated_at: datetime
    model: ModelInfo
    companies: list[CompanyResult]

    @field_serializer("generated_at")
    def _serialize_generated_at(self, value: datetime) -> str:
        # The spec example uses trailing 'Z' for UTC; Pydantic's default would emit
        # '+00:00'. Normalize so the artifact matches the spec example verbatim.
        if value.tzinfo is None:
            return value.replace(microsecond=0).isoformat() + "Z"
        return (
            value.astimezone(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )
