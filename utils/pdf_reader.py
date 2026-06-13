"""
pdf_reader.py — Extracts text from an uploaded PDF resume.

This module uses PyPDF2 to read every page of the uploaded PDF
and returns all the text as a single string.
"""

from PyPDF2 import PdfReader
import io


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Accept a Streamlit UploadedFile object (or any file-like object),
    read every page with PyPDF2, and return the concatenated text.

    Parameters
    ----------
    uploaded_file : streamlit.runtime.uploaded_file_manager.UploadedFile
        The PDF file uploaded by the user via st.file_uploader.

    Returns
    -------
    str
        The full text extracted from every page of the PDF.

    Raises
    ------
    ValueError
        If the PDF contains no extractable text (e.g. scanned image-only PDF).
    Exception
        If PyPDF2 cannot read the file (corrupted / encrypted / not a PDF).
    """

    try:
        # ----------------------------------------------------------
        # 1. Wrap the uploaded bytes in a BytesIO stream so PyPDF2
        #    can treat it like a regular file on disk.
        # ----------------------------------------------------------
        pdf_stream = io.BytesIO(uploaded_file.read())

        # ----------------------------------------------------------
        # 2. Create a PdfReader — this parses the PDF structure.
        # ----------------------------------------------------------
        reader = PdfReader(pdf_stream)

        # ----------------------------------------------------------
        # 3. Loop through every page and collect the text.
        # ----------------------------------------------------------
        all_text_parts: list[str] = []

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            if page_text:                       # skip blank pages
                all_text_parts.append(page_text)

        # ----------------------------------------------------------
        # 4. Join everything into one big string.
        # ----------------------------------------------------------
        full_text = "\n".join(all_text_parts).strip()

        # ----------------------------------------------------------
        # 5. Safety check — if we got nothing, the PDF might be a
        #    scanned image (no selectable text).
        # ----------------------------------------------------------
        if not full_text:
            raise ValueError(
                "The PDF appears to contain no selectable text. "
                "It might be a scanned image. Please upload a "
                "text-based PDF resume."
            )

        return full_text

    except ValueError:
        # Re-raise our own ValueError so the caller can show it to the user.
        raise

    except Exception as exc:
        # Catch anything else (corrupted file, encrypted PDF, etc.)
        raise Exception(
            f"Could not read the PDF file. It may be corrupted or encrypted. "
            f"Details: {exc}"
        ) from exc
