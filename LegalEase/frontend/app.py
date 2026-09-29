import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

load_dotenv(ROOT / ".env")

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

LOGO_PATH = ROOT / "assets" / "logo.png"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .title-container {
        text-align: center;
        padding: 10px 0 25px 0;
    }

    .title-container h1 {
        font-size: 42px;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 19px;
        color: #777;
    }

    .document-card {
        background: #ffffff;
        border: 1px solid #dddddd;
        border-radius: 12px;
        padding: 30px;
        margin-top: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }

    .preview-card {
        background: #fafafa;
        border: 1px solid #dddddd;
        border-radius: 12px;
        padding: 25px;
        margin-top: 20px;
    }

    .disclaimer {
        background: #fff8e1;
        border-left: 5px solid #f0ad00;
        padding: 12px 16px;
        border-radius: 5px;
        margin: 15px 0;
        color: #5f4b00;
    }

    .footer {
        text-align: center;
        color: #888;
        margin-top: 40px;
        padding: 20px;
        border-top: 1px solid #ddd;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=100)

    st.markdown(
        """
        <div class="title-container">
            <h1>⚖️ LegalEase</h1>
            <div class="subtitle">
                AI-Powered Legal Document Generator
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="disclaimer">
    <strong>Important:</strong> LegalEase generates editable legal-document
    drafts using AI. The generated content should be reviewed by a qualified
    legal professional before being used for an actual legal matter.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "document" not in st.session_state:
    st.session_state.document = ""

if "document_type" not in st.session_state:
    st.session_state.document_type = ""

if "terms" not in st.session_state:
    st.session_state.terms = ""

if "effective_date" not in st.session_state:
    st.session_state.effective_date = ""


# ============================================================
# INPUT SECTION
# ============================================================

st.markdown("## 📄 Create Your Legal Document")

with st.container():

    col1, col2 = st.columns(2)

    with col1:

        document_type = st.selectbox(
            "Document Type",
            [
                "Employment Agreement",
                "Lease Agreement",
                "Non-Disclosure Agreement (NDA)",
                "Service Agreement",
                "Freelance Agreement",
                "Partnership Agreement",
                "Sales Agreement",
                "Rental Agreement",
                "Custom Legal Document",
            ],
        )

    with col2:

        effective_date = st.text_input(
            "Effective Date",
            placeholder="Example: 1 October 2026",
        )

    parties = st.text_area(
        "Parties",
        placeholder=(
            "Example:\n"
            "Employer: ABC Technologies Pvt. Ltd.\n"
            "Employee: John Smith"
        ),
        height=130,
    )

    terms = st.text_area(
        "Key Terms",
        placeholder=(
            "Enter the important terms.\n\n"
            "Example:\n"
            "Salary ₹30,000 per month; "
            "Working hours 9 AM to 6 PM; "
            "Probation 6 months; "
            "Confidentiality required"
        ),
        height=180,
    )


# ============================================================
# GENERATE BUTTON
# ============================================================

if st.button(
    "✨ Generate Legal Document",
    type="primary",
    use_container_width=True,
):

    if not parties.strip():
        st.error("Please enter the parties.")

    elif not terms.strip():
        st.error("Please enter the key terms.")

    elif not effective_date.strip():
        st.error("Please enter the effective date.")

    else:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date,
        }

        try:

            with st.spinner("Generating your legal document..."):

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=120,
                )

            if response.status_code == 200:

                data = response.json()

                st.session_state.document = data.get(
                    "content",
                    ""
                )

                st.session_state.document_type = document_type
                st.session_state.terms = terms
                st.session_state.effective_date = effective_date

                st.success(
                    "✅ Legal document generated successfully!"
                )

            else:

                st.error(
                    f"Backend error: {response.status_code}"
                )

                st.code(response.text)

        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Cannot connect to the LegalEase backend."
            )

            st.info(
                "Make sure the FastAPI server is running on "
                "http://127.0.0.1:8000"
            )

        except requests.exceptions.Timeout:

            st.error(
                "❌ The request took too long. "
                "Please try again."
            )

        except Exception as exc:

            st.error(
                f"Unexpected error: {exc}"
            )


# ============================================================
# DOCUMENT EDITOR
# ============================================================

if st.session_state.document:

    st.markdown("---")

    st.markdown("## ✏️ Edit Your Document")

    edited_document = st.text_area(
        "Generated Legal Document",
        value=st.session_state.document,
        height=600,
    )

    st.session_state.document = edited_document


    # ========================================================
    # PREVIEW
    # ========================================================

    st.markdown("## 👁️ Document Preview")

    preview_text = (
        st.session_state.document
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )

    st.markdown(
        f"""
        <div class="preview-card">
            {preview_text}
        </div>
        """,
        unsafe_allow_html=True,
    )


    # ========================================================
    # DOWNLOAD SECTION
    # ========================================================

    st.markdown("---")

    st.markdown("## 📥 Download Document")

    export_payload = {
        "document_type": st.session_state.document_type,
        "content": st.session_state.document,
        "terms": st.session_state.terms,
        "effective_date": st.session_state.effective_date,
    }

    col1, col2, col3 = st.columns(3)


    # TXT
    with col1:

        if st.button(
            "📄 Prepare TXT",
            use_container_width=True,
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/export",
                    params={"file_format": "txt"},
                    json=export_payload,
                    timeout=120,
                )

                if response.status_code == 200:

                    st.download_button(
                        "⬇️ Download TXT",
                        data=response.content,
                        file_name="LegalEase_Document.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )

                else:

                    st.error(response.text)

            except Exception as exc:

                st.error(str(exc))


    # DOCX
    with col2:

        if st.button(
            "📝 Prepare DOCX",
            use_container_width=True,
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/export",
                    params={"file_format": "docx"},
                    json=export_payload,
                    timeout=120,
                )

                if response.status_code == 200:

                    st.download_button(
                        "⬇️ Download DOCX",
                        data=response.content,
                        file_name="LegalEase_Document.docx",
                        mime=(
                            "application/vnd.openxmlformats-"
                            "officedocument.wordprocessingml.document"
                        ),
                        use_container_width=True,
                    )

                else:

                    st.error(response.text)

            except Exception as exc:

                st.error(str(exc))


    # PDF
    with col3:

        if st.button(
            "📕 Prepare PDF",
            use_container_width=True,
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/export",
                    params={"file_format": "pdf"},
                    json=export_payload,
                    timeout=120,
                )

                if response.status_code == 200:

                    st.download_button(
                        "⬇️ Download PDF",
                        data=response.content,
                        file_name="LegalEase_Document.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

                else:

                    st.error(response.text)

            except Exception as exc:

                st.error(str(exc))


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        <strong>LegalEase</strong><br>
        AI-Powered Legal Document Generator<br><br>
        Generated documents are drafts and should be reviewed
        by a qualified legal professional.
    </div>
    """,
    unsafe_allow_html=True,
)