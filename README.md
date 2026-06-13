# 📄 AI Resume Analyzer

An **AI-powered Resume Analyzer** built with Python, Streamlit, PyPDF2, and Google Gemini API. Upload any resume PDF and instantly receive:

- 🎯 **ATS Score** — How well your resume passes Applicant Tracking Systems
- 🎤 **Interview Readiness** — How prepared you appear for interviews
- 💪 **Strengths** — What makes your resume stand out
- 🔍 **Missing Skills** — Key skills you should add
- 🚀 **Improvements** — Actionable suggestions to boost your resume

> **Target Audience:** Students, Job Seekers, Freshers, Career Switchers

---

## 🏗️ Architecture

```
Resume PDF  →  PyPDF2 (pdf_reader.py)  →  Raw Text
                                              ↓
                                    Gemini API (gemini_service.py)
                                    + ATS Prompt (ats_prompt.txt)
                                              ↓
                                        JSON Response
                                              ↓
                                    Streamlit Dashboard (app.py)
                                    ├── ATS Score
                                    ├── Interview Readiness
                                    ├── Strengths
                                    ├── Missing Skills
                                    └── Improvements
```

---

## 📁 Folder Structure

```
AI Resume Analyzer/
├── app.py                   # Streamlit UI & orchestration
├── requirements.txt         # Python dependencies
├── .env                     # API key (you must fill this in)
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── prompts/
│   └── ats_prompt.txt       # Gemini prompt template
├── utils/
│   ├── __init__.py          # Package init
│   ├── pdf_reader.py        # PDF text extraction
│   └── gemini_service.py    # Gemini API integration
└── sample_resumes/          # Place test PDFs here
```

---

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd "AI Resume Analyzer"
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key

1. Get a **free** API key at [Google AI Studio](https://aistudio.google.com/apikey).
2. Open the `.env` file and replace `your_api_key_here` with your actual key:

```
GEMINI_API_KEY=AIzaSy...your_key_here
```

### 5. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🔧 Configuration

| Variable        | File   | Description                            |
| --------------- | ------ | -------------------------------------- |
| `GEMINI_API_KEY` | `.env` | Your Google Gemini API key (required)  |

**Model used:** `gemini-2.0-flash` — fast, free-tier friendly, excellent JSON output.

---

## 🧪 Testing

1. Place a sample resume PDF in the `sample_resumes/` folder.
2. Upload it via the sidebar in the Streamlit app.
3. Click **Analyze Resume** and verify all five result sections appear.
4. Test error cases:
   - Upload a non-PDF file → should show a validation error.
   - Upload with no API key → should show a configuration error.
   - Upload a blank/scanned PDF → should show a "no text found" error.

---

## 📦 Dependencies

| Package               | Purpose                          |
| --------------------- | -------------------------------- |
| `streamlit`           | Web UI framework                 |
| `PyPDF2`              | PDF text extraction              |
| `google-generativeai` | Google Gemini API client         |
| `python-dotenv`       | Load environment variables       |

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

---

<p align="center">Built with ❤️ using Streamlit & Google Gemini AI</p>
