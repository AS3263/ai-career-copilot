# AI Career Copilot

A Streamlit app that compares your resume to a job description and helps you practise interviews.

## Features
- Upload a PDF resume and paste a job description
- Job match percentage with metric cards
- Matched and missing skills
- Generated interview questions
- Answer the questions and get scores and feedback

## Tech
Python, Streamlit, pypdf, and the OpenAI Python library. It works with Google Gemini, Groq or OpenAI, chosen from the sidebar.

## Getting an API key
- Google Gemini (free tier): aistudio.google.com
- Groq (free tier): console.groq.com
- OpenAI (paid): platform.openai.com

## Run it
```bash
pip install -r requirements.txt
streamlit run app.py
```

Pick a provider in the sidebar and paste your key. You can also set it as an environment variable so the box is pre-filled:

```bash
export GEMINI_API_KEY="your-key"   # or GROQ_API_KEY / OPENAI_API_KEY
```

In GitHub Codespaces, open the Ports tab and open port 8501 to view the app.

## Notes
- Only text-based PDFs work. Scanned image PDFs have no readable text.
- Model names change over time. If a model is rejected, edit the Model box in the sidebar.
- Never commit your API key to the repository.
