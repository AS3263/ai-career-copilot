# 🚀 AI Career Copilot

A beginner-friendly Streamlit app that compares your resume to a job description and helps you practise interviews.

## Features
- Upload a PDF resume
- Paste a job description
- Job match percentage + metric cards
- Matched and missing skills
- AI-generated interview questions
- Answer the questions, get scores and feedback

## Tech
Python, Streamlit, OpenAI API, pypdf

## Run it in GitHub Codespaces

1. Create a repo, open it in a Codespace, and add `app.py`, `requirements.txt`, `README.md`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key (pick one):
   - **Codespaces secret (recommended):** GitHub → Settings → Codespaces → Secrets → add `OPENAI_API_KEY`, give it access to this repo, then restart the Codespace.
   - **Terminal:** `export OPENAI_API_KEY="sk-..."`
   - **In the app:** paste it into the sidebar box.
4. Start the app:
   ```bash
   streamlit run app.py
   ```
5. Click the "Open in Browser" popup, or open the **Ports** tab and open port 8501.

## Run locally
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."   # Windows PowerShell: $env:OPENAI_API_KEY="sk-..."
streamlit run app.py
```

## Notes
- Works with text-based PDFs only (scanned image PDFs have no readable text).
- Never commit your API key. Use secrets or environment variables.
- Change the model by editing `MODEL` at the top of `app.py`.
