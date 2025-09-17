# Job Tracker Application

This is a full-stack application designed to help you track and manage job applications. It consists of a Next.js frontend and a Python (FastAPI) backend.

## Features

- **Frontend:** A modern, responsive UI built with Next.js, React, TypeScript, and Tailwind CSS.
- **Backend:** A powerful Python API using FastAPI that ingests job data from Gmail and external job boards via RapidAPI.
- **CV Analysis:** Processes uploaded CVs to extract keywords for better job matching.
- **Database:** Uses a PostgreSQL database to store job application data.

## Project Structure

- **/frontend**: Contains the Next.js frontend application.
- **/backend**: Contains the Python FastAPI backend application.

## Prerequisites

- [Node.js](https://nodejs.org/) (v18 or later) and npm
- [Python](https://www.python.org/) (v3.10 or later) and pip
- [Git](https://git-scm.com/)

## Installation & Setup

All commands should be run from the project's root directory (`job-tracker`).

### 1. Backend (Python / FastAPI)

The backend server handles data aggregation, CV processing, and database interactions.

**a. Create a virtual environment:**
```bash
# For macOS/Linux:
python3 -m venv backend/.venv

# For Windows:
python -m venv backend\.venv
```

**b. Activate the virtual environment:**
- For macOS/Linux:
  ```bash
  source backend/.venv/bin/activate
  ```
- For Windows:
  ```bash
  backend\.venv\Scripts\activate
  ```
  *(You'll need to activate this environment in any new terminal before running backend commands.)*

**c. Install dependencies:**
```bash
pip install -r backend/requirements.txt
```

**d. Set up environment variables:**
Create a file named `.env` inside the `backend` directory and add the following, replacing the placeholder with your actual database connection string:
```
# backend/.env
DATABASE_URL="postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE"
```
- **Note:** You need a running PostgreSQL server.

**e. Set up Google API Credentials:**
1.  Follow the [Google Cloud instructions](https://developers.google.com/workspace/guides/create-credentials) to create an OAuth 2.0 Client ID.
2.  Download the `credentials.json` file and place it in the `backend` directory.
3.  The first time you run a script that uses the Gmail API, you will be prompted to authorize the application. This will create a `token.pickle` file in the root directory.

**f. Set up RapidAPI Key:**
To fetch jobs from the external API, you need to get an API key from [RapidAPI](https://rapidapi.com/). You will need to modify `backend/rapidapi_jobs.py` to include your key.

### 2. Frontend (Next.js / React)

The frontend provides the user interface for the application.

**a. Install dependencies:**
```bash
npm install --prefix frontend
```

## Running the Application

You need to run both the backend and frontend servers simultaneously from the project root.

**1. Start the Backend Server:**
- Make sure your Python virtual environment is activated (see setup steps above).
- From the project root, run the Uvicorn server:
  ```bash
  python -m uvicorn backend.main:app --reload --port 8000
  ```
- The backend API will be available at `http://localhost:8000`.

**2. Start the Frontend Server:**
- Open a new terminal in the project root.
- Run the Next.js development server:
  ```bash
  npm run dev --prefix frontend
  ```
- The frontend application will be available at `http://localhost:3000`.

## Usage

Once both servers are running, open your web browser and go to `http://localhost:3000`. From there you can:
- View and filter job postings.
- See details for each job.
- Upload your CV for analysis.
