# SkillGap

SkillGap is an AI + Data Science Career Intelligence Platform designed to analyze your professional profile against the live job market and provide actionable, real-time feedback and learning roadmaps.

## Architecture

- **Backend (REST API)**: Built with FastAPI (`src/skillgap/api/main.py`), utilizing TF-IDF cosine similarity, experience parsing, and structured NLP skill-matching.
- **Frontend (Interactive Dashboard)**: Built with Vanilla HTML/CSS/JS (`src/skillgap/dashboard/`), featuring a dark-themed space aesthetic, glowing radial progress indicators, and real-time client-side scoring updates.
- **Job Aggregators**: Fetches remote and local job opportunities concurrently across several providers (Remotive, Himalayas, WeWorkRemotely, Adzuna, Findwork, RemoteOK, Arbeitnow).

## Getting Started

1. **Environment Setup**:
   Ensure you have a `.env` file containing your `GROQ_API_KEY`.
   ```env
   GROQ_API_KEY=gsk_...
   ```

2. **Start the FastAPI server**:
   Run the FastAPI application from the project root:
   ```bash
   .venv\Scripts\python.exe -m skillgap.api.main
   ```

3. **Open the Dashboard**:
   Go to **[http://localhost:8000](http://localhost:8000)** in your browser.
   - Upload your resume PDF (`sample_data/resume.pdf` is provided for testing).
   - Search for a keyword like `python` (which filters strictly by job title).
   - See the matched list ranked automatically by score, highlighting your **Best Fit**!
   - Select a job and click **Analyze Requirements with AI Recruiter** to extract skills on-demand.
   - Interact with the checklist to recalculate your projected score in real-time.
