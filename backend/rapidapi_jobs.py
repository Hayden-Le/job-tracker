
import os
import httpx
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import hashlib
from pathlib import Path

# Load .env from the correct location (backend/.env)
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from backend.db import async_sessionmaker
from backend.models import JobPost

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
if not RAPIDAPI_KEY:
    raise ValueError("RAPIDAPI_KEY environment variable not set")

API_HOST = "jsearch.p.rapidapi.com"
SEARCH_ENDPOINT = "https://jsearch.p.rapidapi.com/search"
DETAILS_ENDPOINT = "https://jsearch.p.rapidapi.com/job-details"

async def fetch_job_details(job_id: str, client: httpx.AsyncClient) -> dict | None:
    """Fetches the full details for a single job."""
    querystring = {"job_id": job_id, "extended_publisher_details": "false"}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": API_HOST,
    }
    try:
        response = await client.get(DETAILS_ENDPOINT, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK" and data.get("data"):
            return data["data"][0]
    except httpx.HTTPStatusError as e:
        print(f"HTTP error fetching details for job {job_id}: {e}")
    except Exception as e:
        print(f"Error fetching details for job {job_id}: {e}")
    return None

async def search_jobs(query: str = "Python developer in USA", num_pages: int = 1):
    """Searches for jobs and saves them to the database."""
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": API_HOST,
    }
    
    async with httpx.AsyncClient() as client:
        for page in range(1, num_pages + 1):
            querystring = {"query": query, "page": str(page), "num_pages": "1"}
            print(f"Fetching page {page} for query: '{query}'")
            
            try:
                search_response = await client.get(SEARCH_ENDPOINT, headers=headers, params=querystring)
                search_response.raise_for_status()
                search_data = search_response.json()

                if search_data["status"] != "OK" or not search_data.get("data"):
                    print("No jobs found or API error.")
                    continue

                jobs_to_create = []
                for job_summary in search_data["data"]:
                    job_id = job_summary.get("job_id")
                    if not job_id:
                        continue

                    # Use a consistent hash key for deduplication
                    hash_key = hashlib.sha256(f"jsearch_{job_id}".encode()).hexdigest()

                    async with async_sessionmaker() as session:
                        existing_job = await session.get(JobPost, hash_key)
                        if existing_job:
                            print(f"Job {job_id} already exists, skipping.")
                            continue
                    
                    print(f"Fetching details for job_id: {job_id}")
                    details = await fetch_job_details(job_id, client)
                    
                    if not details:
                        print(f"Could not fetch details for {job_id}, skipping.")
                        continue

                    # --- Map API response to JobPost model ---
                    description_text = details.get("job_description", "No description provided.")
                    
                    # Create a simple structured description
                    description_sections = {
                        "description": description_text.split('\n\n') # Split into paragraphs
                    }

                    posted_at_timestamp = details.get("job_posted_at_timestamp")
                    posted_at = datetime.fromtimestamp(posted_at_timestamp) if posted_at_timestamp else None

                    job_post = JobPost(
                        hash_key=hash_key,
                        source="JSearch",
                        title=details.get("job_title"),
                        company=details.get("employer_name"),
                        location=details.get("job_city"),
                        description_snippet=details.get("job_description", "")[:250] + "...",
                        description_sections=description_sections,
                        posted_at=posted_at,
                        canonical_url=details.get("job_apply_link"),
                        salary_text=details.get("job_salary_range"),
                        is_active=True,
                    )
                    jobs_to_create.append(job_post)

                if jobs_to_create:
                    async with async_sessionmaker() as session:
                        print(f"Adding {len(jobs_to_create)} new jobs to the database.")
                        session.add_all(jobs_to_create)
                        await session.commit()
                else:
                    print("No new jobs to add on this page.")

            except httpx.HTTPStatusError as e:
                print(f"HTTP error during search: {e}")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

if __name__ == "__main__":
    # Example of how to run the script
    # You can change the query and number of pages here
    asyncio.run(search_jobs(query="Software Engineer in New York, NY", num_pages=2))
