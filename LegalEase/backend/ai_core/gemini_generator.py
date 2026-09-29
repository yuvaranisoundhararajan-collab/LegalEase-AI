from __future__ import annotations

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ---------------------------------------------------------
# Load .env from the LegalEase project root
# ---------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"

load_dotenv(ENV_FILE)


class GeminiDocumentGenerator:
    """
    Generates legal-document drafts using the Gemini API.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. "
                "Please add your Gemini API key to the .env file."
            )

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash",
        ).strip()

        self.client = genai.Client(
            api_key=self.api_key
        )

    # ---------------------------------------------------------
    # Prompt
    # ---------------------------------------------------------
    def _build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:

        return f"""
You are an AI legal-document drafting assistant.

Create a professional, editable legal document based ONLY
on the information supplied by the user.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

EFFECTIVE DATE:
{effective_date}

KEY TERMS:
{terms}

IMPORTANT RULES:

1. Do not invent names, addresses, dates, amounts, companies,
   jurisdictions, or other facts.

2. If important information is missing, use:
   [TO BE COMPLETED]

3. Create a complete and professionally structured document.

4. Include appropriate sections for the selected document type.

5. Use clear legal-document language.

6. Include signature blocks where appropriate.

7. Use headings and numbered sections where useful.

8. Preserve all user-provided facts accurately.

9. Do not provide explanations before or after the document.

10. Do not use Markdown code fences.

11. Do not claim that the document is legally valid or
    enforceable in a particular jurisdiction.

12. Add this short notice near the end:

   "This document is an AI-generated draft for informational
   purposes and should be reviewed by a qualified legal
   professional before use."

Return ONLY the document text.
"""

    # ---------------------------------------------------------
    # Generate document with automatic retry
    # ---------------------------------------------------------
    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:

        prompt = self._build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            effective_date=effective_date,
        )

        # Retry delays: 2s, 4s, 8s, 16s
        retry_delays = [2, 4, 8, 16]

        last_error = None

        for attempt in range(len(retry_delays) + 1):

            try:

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.35,
                        max_output_tokens=12000,
                    ),
                )

                text = getattr(response, "text", None)

                if not text or not text.strip():
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return text.strip()

            except Exception as exc:

                last_error = exc

                error_text = str(exc)

                # Retry only temporary service errors.
                is_temporary_error = (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                    or "500" in error_text
                    or "INTERNAL" in error_text
                )

                if not is_temporary_error:
                    raise RuntimeError(
                        f"Gemini API request failed: {exc}"
                    ) from exc

                # No more retries
                if attempt >= len(retry_delays):
                    break

                delay = retry_delays[attempt]

                print(
                    f"Gemini temporary error detected. "
                    f"Retrying in {delay} seconds..."
                )

                time.sleep(delay)

        raise RuntimeError(
            "Gemini API is temporarily unavailable after "
            "multiple retry attempts. "
            "Please wait a few minutes and try Generate again. "
            f"Last error: {last_error}"
        )