import os
import shutil
import tempfile
from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from skillgap.models.resume import ResumeProfile
from skillgap.models.job import JobPosting
from skillgap.services.resume_service import ResumeService
from skillgap.services.jobs.job_aggregator_service import JobAggregatorService
from skillgap.services.jobs.job_skill_extraction_service import JobSkillExtractionService
from skillgap.services.matching.skill_gap_service import SkillGapService

app = FastAPI(title="SkillGap API", description="AI & Data Science Career Intelligence Platform API")

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request bodies
class EnrichRequest(BaseModel):
    title: str
    company: str
    location: str
    source: str
    url: str
    description: str = ""
    salary: str = ""
    remote: bool = False
    posted_date: str = ""

class MatchRequest(BaseModel):
    profile: dict
    job: dict


class SearchRequest(BaseModel):
    keyword: str
    profile: dict = None


@app.post("/api/profile/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    Accepts a PDF resume, parses it using LLM, maps it to a profile,
    and discards the file immediately for privacy.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Write to a temporary file
    temp_dir = tempfile.gettempdir()
    base_name = os.path.basename(file.filename)
    temp_path = os.path.join(temp_dir, base_name)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the resume
        profile = ResumeService.process_resume(temp_path)
        
        # Convert dataclass to dict
        profile_dict = {
            "name": profile.name,
            "email": profile.email,
            "phone": profile.phone,
            "summary": profile.summary,
            "education": profile.education,
            "experience": profile.experience,
            "projects": profile.projects,
            "skills": profile.skills,
            "certifications": profile.certifications,
            "awards": profile.awards,
            "organizations": profile.organizations,
            "languages": profile.languages
        }
        return profile_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Delete temporary file (privacy-first)
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/api/jobs/search")
async def search_jobs(req: SearchRequest):
    """
    Queries live job providers concurrently, deduplicates results, and returns them.
    """
    try:
        aggregator = JobAggregatorService()
        jobs = aggregator.fetch_jobs(req.keyword)
        
        # Parse profile if provided
        profile = None
        if req.profile:
            try:
                p = req.profile
                profile = ResumeProfile(
                    name=p.get("name", ""),
                    email=p.get("email", ""),
                    phone=p.get("phone", ""),
                    summary=p.get("summary", ""),
                    education=p.get("education", []),
                    experience=p.get("experience", []),
                    projects=p.get("projects", []),
                    skills=p.get("skills", {}),
                    certifications=p.get("certifications", []),
                    awards=p.get("awards", []),
                    organizations=p.get("organizations", []),
                    languages=p.get("languages", [])
                )
            except Exception:
                pass

        service = SkillGapService()

        # Convert JobPostings to dictionaries and compute readiness score if profile is available
        results = []
        for job in jobs:
            score = None
            if profile:
                try:
                    # Calculate a fast match score (semantic + experience + skill matching)
                    # Note: job.skills is empty if not enriched, but semantic and experience match work perfectly.
                    analysis = service.analyze_gap(profile, job, market_dataset_path=None)
                    score = round(analysis.get("current_readiness", 0), 1)
                except Exception:
                    pass

            results.append({
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "source": job.source,
                "url": job.url,
                "description": job.description,
                "salary": job.salary,
                "remote": job.remote,
                "posted_date": job.posted_date,
                "skills": job.skills,
                "seniority": job.seniority,
                "role_category": job.role_category,
                "industry": job.industry,
                "readiness_score": score
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/search")
async def search_jobs_get(keyword: str = Query(..., min_length=2)):
    """
    Fallback GET endpoint for search to handle caching or simple queries.
    """
    try:
        aggregator = JobAggregatorService()
        jobs = aggregator.fetch_jobs(keyword)
        
        results = []
        for job in jobs:
            results.append({
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "source": job.source,
                "url": job.url,
                "description": job.description,
                "salary": job.salary,
                "remote": job.remote,
                "posted_date": job.posted_date,
                "skills": job.skills,
                "seniority": job.seniority,
                "role_category": job.role_category,
                "industry": job.industry,
                "readiness_score": None
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/api/jobs/enrich")
async def enrich_job(req: EnrichRequest):
    """
    Uses LLM to extract skills, seniority, role category, and industry from a job description.
    """
    try:
        job = JobPosting(
            title=req.title,
            company=req.company,
            location=req.location,
            source=req.source,
            url=req.url,
            description=req.description,
            salary=req.salary,
            remote=req.remote,
            posted_date=req.posted_date
        )
        
        enriched_job = JobSkillExtractionService.enrich(job)
        
        return {
            "title": enriched_job.title,
            "company": enriched_job.company,
            "location": enriched_job.location,
            "source": enriched_job.source,
            "url": enriched_job.url,
            "description": enriched_job.description,
            "salary": enriched_job.salary,
            "remote": enriched_job.remote,
            "posted_date": enriched_job.posted_date,
            "skills": enriched_job.skills,
            "seniority": enriched_job.seniority,
            "role_category": enriched_job.role_category,
            "industry": enriched_job.industry
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/match")
async def match_skills(req: MatchRequest):
    """
    Calculates current readiness, skill gaps, course recommendations with confidence,
    and projected readiness scores.
    """
    try:
        # Reconstruct resume profile
        profile = ResumeProfile(
            name=req.profile.get("name", ""),
            email=req.profile.get("email", ""),
            phone=req.profile.get("phone", ""),
            summary=req.profile.get("summary", ""),
            education=req.profile.get("education", []),
            experience=req.profile.get("experience", []),
            projects=req.profile.get("projects", []),
            skills=req.profile.get("skills", {}),
            certifications=req.profile.get("certifications", []),
            awards=req.profile.get("awards", []),
            organizations=req.profile.get("organizations", []),
            languages=req.profile.get("languages", [])
        )
        
        # Reconstruct job posting
        j = req.job
        job = JobPosting(
            title=j.get("title", ""),
            company=j.get("company", ""),
            location=j.get("location", ""),
            source=j.get("source", ""),
            url=j.get("url", ""),
            description=j.get("description", ""),
            salary=j.get("salary", ""),
            remote=j.get("remote", False),
            posted_date=j.get("posted_date", ""),
            skills=j.get("skills", []),
            seniority=j.get("seniority", ""),
            role_category=j.get("role_category", ""),
            industry=j.get("industry", "")
        )

        dataset_path = "data/jobs/jobs.json"
        if not os.path.exists(dataset_path):
            dataset_path = None

        service = SkillGapService()
        analysis = service.analyze_gap(profile, job, market_dataset_path=dataset_path)
        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve dashboard files from root
dashboard_dir = Path(__file__).parents[1] / "dashboard"
if not dashboard_dir.exists():
    dashboard_dir = Path("src/skillgap/dashboard")

if dashboard_dir.exists():
    app.mount("/", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")
else:
    print(f"Warning: Dashboard directory not found at {dashboard_dir.absolute()}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("skillgap.api.main:app", host="0.0.0.0", port=8000, reload=True)
