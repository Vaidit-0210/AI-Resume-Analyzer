"""
gemini_service.py — Communicates with Google Gemini to analyze resume text.

This module:
  1. Loads the Gemini API key from the .env file.
  2. Reads the ATS prompt template from prompts/ats_prompt.txt.
  3. Sends the resume text + prompt to Gemini and parses the JSON response.
"""

import json
import os
import re
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

# ------------------------------------------------------------------
# 1. Load environment variables from .env (must contain GEMINI_API_KEY)
# ------------------------------------------------------------------
load_dotenv()

# ------------------------------------------------------------------
# 2. Resolve paths relative to the project root so the module works
#    regardless of which directory the user runs `streamlit run` from.
# ------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH  = PROJECT_ROOT / "prompts" / "ats_prompt.txt"


def _load_prompt_template() -> str:
    """Read the ATS prompt template from disk."""
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Prompt file not found at {PROMPT_PATH}. "
            "Make sure the prompts/ folder exists in the project root."
        )
    return PROMPT_PATH.read_text(encoding="utf-8")


def _extract_json(raw_text: str) -> dict:
    """
    Extract and parse JSON from Gemini's response.

    Gemini sometimes wraps its JSON in ```json ... ``` markdown fences.
    This helper strips those fences and parses the content.

    Parameters
    ----------
    raw_text : str
        The raw response string from Gemini.

    Returns
    -------
    dict
        Parsed JSON as a Python dictionary.

    Raises
    ------
    ValueError
        If JSON cannot be found or parsed.
    """

    # Strip leading/trailing whitespace
    text = raw_text.strip()

    # Remove markdown code fences if present  (```json ... ``` or ``` ... ```)
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    # Attempt to parse
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        # Last-resort: try to find the first { ... } block
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        raise ValueError(
            "Gemini returned a response that could not be parsed as JSON. "
            f"Raw response:\n{raw_text[:500]}"
        ) from exc


def analyze_resume(resume_text: str) -> dict:
    """
    Send the resume text to Google Gemini and return structured analysis.

    Parameters
    ----------
    resume_text : str
        Plain text extracted from the user's resume PDF.

    Returns
    -------
    dict
        A dictionary with keys:
        - ats_score          (int, 0-100)
        - missing_skills     (list[str])
        - strengths          (list[str])
        - improvements       (list[str])
        - interview_readiness (int, 0-100)

    Raises
    ------
    EnvironmentError
        If GEMINI_API_KEY is not set in .env.
    Exception
        If the Gemini API call fails.
    """

    # ----------------------------------------------------------
    # A. Validate API key
    # ----------------------------------------------------------
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        raise EnvironmentError(
            "GEMINI_API_KEY is not configured. "
            "Please add your key to the .env file in the project root.\n"
            "Get a free key at: https://aistudio.google.com/apikey"
        )

    # ----------------------------------------------------------
    # B. Configure the Gemini client
    # ----------------------------------------------------------
    genai.configure(api_key=api_key)

    # ----------------------------------------------------------
    # C. Build the full prompt by injecting resume text
    # ----------------------------------------------------------
    prompt_template = _load_prompt_template()
    full_prompt = prompt_template.replace("{resume_text}", resume_text)

    # ----------------------------------------------------------
    # D. Call Gemini (using gemini-2.5-flash — latest model)
    # ----------------------------------------------------------
    model = genai.GenerativeModel("gemini-2.5-flash")

    try:
        response = model.generate_content(full_prompt)
    except Exception as api_err:
        err_msg = str(api_err)
        if "429" in err_msg or "quota" in err_msg.lower():
            raise Exception(
                "🚫 Gemini API quota exceeded. This can happen if:\n"
                "• Your free-tier daily limit has been reached — wait a minute and try again.\n"
                "• The API key is brand-new — it may take a few minutes to activate.\n"
                "• Visit https://ai.google.dev/gemini-api/docs/rate-limits for details."
            ) from api_err
        raise

    # ----------------------------------------------------------
    # E. Parse the JSON response
    # ----------------------------------------------------------
    result = _extract_json(response.text)

    # ----------------------------------------------------------
    # F. Validate expected keys (provide safe defaults)
    # ----------------------------------------------------------
    expected_keys = {
        "ats_score": 0,
        "missing_skills": [],
        "strengths": [],
        "improvements": [],
        "interview_readiness": 0,
    }
    for key, default in expected_keys.items():
        if key not in result:
            result[key] = default

    return result
