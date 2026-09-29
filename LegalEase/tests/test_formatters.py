from backend.utils.document_formatter import (
    sanitize_text,
    format_txt,
    format_docx,
    format_pdf
)


def test_sanitize_text():

    result = sanitize_text(
        "Hello\u2014world\r\n\r\n\r\n"
    )

    assert result == "Hello-world"


def test_txt_export():

    result = format_txt(
        "Test document"
    )

    assert result == (
        b"Test document\n"
    )


def test_docx_export():

    result = format_docx(

        "1. Introduction\n\n"
        "This is a test.",

        "Test Agreement",

        "Payment within 30 days;"
        "Confidentiality",

        "2026-09-26"
    )

    assert result[:2] == b"PK"


def test_pdf_export():

    result = format_pdf(

        "1. Introduction\n\n"
        "This is a test.",

        "Test Agreement",

        "Payment within 30 days;"
        "Confidentiality",

        "2026-09-26"
    )

    assert result.startswith(
        b"%PDF"
    )