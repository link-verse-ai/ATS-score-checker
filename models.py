from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from datetime import date

class ContactInfo(BaseModel):
    fullName: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    zipCode: str
    country: str
    linkedIn: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    portfolio: Optional[HttpUrl] = None
    otherWebsites: Optional[Dict[str, HttpUrl]] = {}

class Summary(BaseModel):
    content: str
    rawSummary: str

class Experience(BaseModel):
    position: str
    company: str
    location: str
    startDate: date
    endDate: Optional[date] = None
    current: bool
    description: List[str]
    rawDescription: List[str]
    achievements: List[str]
    technologies: List[str]

class Education(BaseModel):
    institution: str
    degree: str
    fieldOfStudy: str
    location: str
    startDate: date
    endDate: Optional[date] = None
    minor: Optional[str] = None
    current: bool
    gpa: Optional[str] = None
    description: List[str]
    rawDescription: List[str]
    achievements: List[str]

class Skill(BaseModel):
    names: List[str]
    category: str

class Project(BaseModel):
    title: str
    description: List[str]
    rawDescription: List[str]
    role: str
    organization: str
    url: Optional[HttpUrl] = None
    startDate: date
    endDate: Optional[date] = None
    current: bool
    technologies: List[str]
    achievements: List[str]

class Certification(BaseModel):
    name: str
    issuer: str
    issueDate: date
    expiryDate: Optional[date] = None
    credentialId: Optional[str] = None
    credentialUrl: Optional[HttpUrl] = None
    description: Optional[str] = None
    rawDescription: List[str]

class Language(BaseModel):
    name: str
    proficiency: str

class Award(BaseModel):
    title: str
    issuer: str
    date: date
    description: Optional[str] = None
    rawDescription: List[str]

class Publication(BaseModel):
    title: str
    publisher: str
    publicationDate: date
    authors: List[str]
    url: Optional[HttpUrl] = None
    description: Optional[str] = None
    rawDescription: List[str]

class ResumeSchema(BaseModel):
    jobDescription: str
    targetPosition: str
    targetCompany: str
    contactInfo: ContactInfo
    summary: Summary
    experiences: List[Experience]
    educations: List[Education]
    skills: List[Skill]
    projects: List[Project]
    certifications: List[Certification]
    languages: List[Language]
    awards: List[Award]
    publications: List[Publication]

class ATSResponse(BaseModel):
    score: float
    matches: List[str]
    missing_keywords: List[str]
    suggestions: List[str]
    formatting_warnings: List[str]