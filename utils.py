import spacy
from typing import List, Dict
from models import ResumeSchema
import concurrent.futures
from faang_data import FAANG_KEYWORDS, COMPANY_PREFERENCES

nlp = spacy.load("en_core_web_lg")

def extract_resume_text(resume: ResumeSchema) -> str:
    text_parts = []
    text_parts.append(resume.summary.content)
    text_parts.append(resume.summary.rawSummary)
    for exp in resume.experiences:
        text_parts.extend(exp.description)
        text_parts.extend(exp.rawDescription)
        text_parts.extend(exp.achievements)
        text_parts.extend(exp.technologies)
    for edu in resume.educations:
        text_parts.extend(edu.description)
        text_parts.extend(edu.rawDescription)
        text_parts.extend(edu.achievements)
    for skill in resume.skills:
        text_parts.extend(skill.names)
    for project in resume.projects:
        text_parts.extend(project.description)
        text_parts.extend(project.rawDescription)
        text_parts.extend(project.technologies)
        text_parts.extend(project.achievements)
    for cert in resume.certifications:
        text_parts.append(cert.description or "")
        text_parts.extend(cert.rawDescription)
    for lang in resume.languages:
        text_parts.append(lang.name)
    for award in resume.awards:
        text_parts.append(award.description or "")
        text_parts.extend(award.rawDescription)
    for pub in resume.publications:
        text_parts.append(pub.description or "")
        text_parts.extend(pub.rawDescription)
    return " ".join([part for part in text_parts if part])

def extract_keywords(text: str) -> List[str]:
    doc = nlp(text.lower())
    keywords = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
            keywords.append(token.text)
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) > 1 and not any(t.is_stop for t in chunk):
            keywords.append(chunk.text)
    return sorted(list(set(keywords)))

def extract_keywords_parallel(texts: List[str]) -> List[str]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(extract_keywords, texts)
    return sorted(list(set().union(*results)))

def get_job_keywords(job_description: str, target_company: str = None) -> List[str]:
    job_keywords = extract_keywords(job_description) if job_description else []
    if target_company:
        company = target_company.lower()
        if company in COMPANY_PREFERENCES:
            job_keywords.extend(COMPANY_PREFERENCES[company])
    return list(set(job_keywords))

def calculate_ats_score(resume_keywords: List[str], job_keywords: List[str], faang_keywords: List[str] = FAANG_KEYWORDS) -> Dict:
    matches = []
    resume_docs = [nlp(kw) for kw in resume_keywords]
    job_docs = [nlp(kw) for kw in job_keywords]
    
    for r_doc in resume_docs:
        for j_doc in job_docs:
            if r_doc.text in matches or j_doc.text in matches:
                continue
            if r_doc.similarity(j_doc) > 0.8:
                matches.append(r_doc.text)
    
    faang_matches = [kw for kw in matches if kw in faang_keywords]
    score = (len(matches) + len(faang_matches)) / (len(job_keywords) + len(faang_keywords)) * 100 if job_keywords or faang_keywords else 0
    
    missing_keywords = [kw for kw in job_keywords if kw not in matches]
    return {
        "score": round(score, 1),
        "matches": matches,
        "missing_keywords": missing_keywords,
        "suggestions": [f"Add '{kw}' to your resume" for kw in missing_keywords]
    }

def check_formatting(resume: ResumeSchema) -> List[str]:
    warnings = []
    if len(resume.experiences) > 5:
        warnings.append("Too many experience entries; ATS may prioritize recent roles. Limit to 5.")
    if not resume.skills:
        warnings.append("Skills section is empty; ATS relies heavily on skills keywords.")
    for exp in resume.experiences:
        if not exp.achievements:
            warnings.append(f"Experience at {exp.company} lacks achievements; add measurable outcomes.")
    return warnings