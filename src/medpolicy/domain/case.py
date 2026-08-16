from datetime import date
from pydantic import BaseModel, Field

class CoverageInfo(BaseModel):
    payer_id : str
    member_id : str
    active: bool 


class Diagnosis(BaseModel):
    code: str
    display: str


class ConservativeTreatment(BaseModel):
    treatment_type: str
    duration_weeks: int = Field(ge=0)
    completed: bool


class PriorImaging(BaseModel):
    service_code: str
    performed_date: date

class PriorAuthCase(BaseModel):
    case_id: str
    patient_id: str
    requested_service_code: str

    coverage: CoverageInfo
    diagnoses: list[Diagnosis]

    treatments: list[ConservativeTreatment] = []
    symptoms_persist: bool | None = None

    prior_imaging: list[PriorImaging] = []


    