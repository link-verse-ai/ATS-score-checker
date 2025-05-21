from fastapi import FastAPI, HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from models import ResumeSchema, ATSResponse
from utils import extract_resume_text, extract_keywords_parallel, calculate_ats_score, check_formatting, get_job_keywords
from faang_data import GENERAL_REQUIREMENTS, FAANG_KEYWORDS

app = FastAPI(title="ATS Checker API")
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://redis:6379")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/check-ats", response_model=ATSResponse)
@limiter.limit("10/minute")
async def check_ats(request: Request, resume: ResumeSchema):
    job_description = resume.jobDescription
    target_position = resume.targetPosition
    target_company = resume.targetCompany
    
    if job_description and target_position and target_company:
        job_keywords = get_job_keywords(job_description, target_company)
    else:
        job_keywords = GENERAL_REQUIREMENTS + FAANG_KEYWORDS
    
    resume_text = extract_resume_text(resume)
    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract meaningful content from resume")
    
    resume_keywords = extract_keywords_parallel([resume_text])
    result = calculate_ats_score(resume_keywords, job_keywords)
    formatting_warnings = check_formatting(resume)
    
    return ATSResponse(
        score=result["score"],
        matches=result["matches"],
        missing_keywords=result["missing_keywords"],
        suggestions=result["suggestions"],
        formatting_warnings=formatting_warnings
    )

@app.get("/")
async def root():
    return {"message": "Welcome to the ATS Checker API. Use /check-ats to analyze a resume."}