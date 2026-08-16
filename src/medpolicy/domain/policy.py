from pydantic import BaseModel, Field



class ImagingPolicy(BaseModel):
    policy_id: str 
    version: str 
    allowed_diagnosis_codes: set[str]

    minimum_conservative_treatment_weeks: int = Field(ge=0)

    duplicate_imaging_window_days: int = Field(ge=0)

