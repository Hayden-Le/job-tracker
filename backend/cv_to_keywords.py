import sys
import os
import json
import httpx
import PyPDF2
import asyncio
from pathlib import Path

# Add project root to path to allow sibling imports
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from backend.rapidapi_jobs import search_jobs

LMSTUDIO_URL = "http://localhost:1234/v1/chat/completions"

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file."""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = "".join(page.extract_text() for page in reader.pages)
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}", file=sys.stderr)
        return ""

def get_job_title_from_lmstudio(cv_text: str) -> str:
    """Sends CV text to LMStudio to extract a job title."""
    if not cv_text:
        return ""

    try:
        client = httpx.Client()
        payload = {
            "model": "mistralai/mistral-7b-instruct-v0.3",
            "messages": [
                {"role": "system", "content": "You are an expert HR assistant. Your task is to extract the most likely job title from the provided CV. Respond with only the job title and nothing else."},
                {"role": "user", "content": cv_text}
            ],
            "temperature": 0.2,
        }
        response = client.post(LMSTUDIO_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        job_title = data['choices'][0]['message']['content'].strip()
        return job_title
    except httpx.RequestError as e:
        print(f"Error calling LMStudio: {e}. Is LMStudio running at {LMSTUDIO_URL}?", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"An error occurred while processing LMStudio response: {e}", file=sys.stderr)
        return ""

async def main():
    if len(sys.argv) < 2:
        print("Usage: python cv_to_keywords.py <filename>", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]
    # The file is saved by Next.js in `frontend/uploads`
    cv_path = project_root / "frontend" / "uploads" / filename

    print(f"Processing CV: {cv_path}")
    cv_text = extract_text_from_pdf(str(cv_path))
    
    if not cv_text:
        print("Could not extract text from CV.", file=sys.stderr)
        sys.exit(1)

    print("Extracting job title from CV using LMStudio...")
    job_title = get_job_title_from_lmstudio(cv_text)

    if not job_title:
        print("Could not determine job title from CV.", file=sys.stderr)
        sys.exit(1)

    print(f"Extracted job title: '{job_title}'. Now searching for jobs...")
    
    # Use the extracted job title to search for jobs
    # The search_jobs function will save the results to the database
    await search_jobs(query=job_title, num_pages=1)

    print(json.dumps({"success": True, "message": f"Job search for '{job_title}' completed successfully."}))

if __name__ == "__main__":
    asyncio.run(main())