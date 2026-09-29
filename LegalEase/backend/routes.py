from io import BytesIO
import re

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from backend.ai_core.gemini_generator import GeminiDocumentGenerator
from backend.schemas import DocumentRequest, DocumentResponse, ExportRequest
from backend.utils.document_formatter import (
    format_docx,
    format_pdf,
    format_txt,
)


# IMPORTANT:
# This router is imported by backend.main
router = APIRouter()


_generator = None


def get_generator():
    global _generator

    if _generator is None:
        _generator = GeminiDocumentGenerator()

    return _generator


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "LegalEase API",
    }


@router.post("/generate", response_model=DocumentResponse)
def generate_document(request: DocumentRequest):
    try:
        generator = get_generator()

        content = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
        )

        return DocumentResponse(
            document_type=request.document_type,
            content=content,
            model=generator.model,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document generation failed: {exc}",
        ) from exc


def safe_filename(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip())
    value = value.strip("_")

    if not value:
        value = "legal_document"

    return value[:80]


@router.post("/export")
def export_document(
    request: ExportRequest,
    file_format: str = Query(
        default="txt",
        pattern="^(txt|docx|pdf)$",
    ),
):
    try:
        filename_base = safe_filename(request.document_type)

        if file_format == "txt":
            file_bytes = format_txt(
                request.content,
                request.document_type,
                request.effective_date,
            )

            return Response(
                content=file_bytes,
                media_type="text/plain",
                headers={
                    "Content-Disposition": (
                        f'attachment; filename="{filename_base}.txt"'
                    )
                },
            )

        if file_format == "docx":
            file_bytes = format_docx(
                content=request.content,
                document_type=request.document_type,
                terms=request.terms,
                effective_date=request.effective_date,
            )

            return Response(
                content=file_bytes,
                media_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                headers={
                    "Content-Disposition": (
                        f'attachment; filename="{filename_base}.docx"'
                    )
                },
            )

        if file_format == "pdf":
            file_bytes = format_pdf(
                content=request.content,
                document_type=request.document_type,
                terms=request.terms,
                effective_date=request.effective_date,
            )

            return Response(
                content=file_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": (
                        f'attachment; filename="{filename_base}.pdf"'
                    )
                },
            )

        raise HTTPException(
            status_code=400,
            detail="Unsupported file format.",
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {exc}",
        ) from exc