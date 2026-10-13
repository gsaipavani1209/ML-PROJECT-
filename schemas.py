
from pydantic import BaseModel


class PerformanceInput(BaseModel):
    university_admission_year: int
    gender: str
    age: int
    hsc_passing_year: int
    program: str
    current_semester: int
    meritorious_scholarship: str
    university_transportation: str
    daily_study_hours: float
    study_sessions_per_day: int
    preferable_learning_mode: str
    smartphone: str
    personal_computer: str
    daily_social_media_hours: float
    english_proficiency: str
    average_attendance: str
    probation: str
    suspension: str
    teacher_consultancy: str
    skills: str
    skill_development_hours: float
    interested_area: str
    relationship_status: str
    cocurriculum_activities: str
    living_status: str
    health_issues: str
    previous_sgpa: float
    physical_disabilities: str
    completed_credits: float
    monthly_family_income: float
