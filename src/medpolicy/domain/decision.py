from enum import Enum
from pydantic import BaseModel


class DecisionStatus(str, Enum):
    APPROVE = "approve"
    DENY = "deny"
    PEND = "pend_for_information"
    HUMAN_REVIEW = "human_review"


class CriterionStatus(str, Enum):
    MET = "met"
    NOT_MET = "not_met"
    UNKNOWN = "unknown"

class CriterionResult(BaseModel):
    criterion_id: str
    description: str
    status: CriterionStatus
    evidence: list[str] = []


class Decision(BaseModel):
    case_id: str
    policy_id: str
    policy_version: str

    status: DecisionStatus

    criteria: list[CriterionResult]

    missing_information: list[str] = []