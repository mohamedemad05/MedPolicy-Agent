from datetime import date

from medpolicy.domain.case import (
    ConservativeTreatment,
    CoverageInfo,
    Diagnosis,
    PriorAuthCase,
    PriorImaging,
)
from medpolicy.domain.decision import (
    CriterionStatus,
    DecisionStatus,
)
from medpolicy.domain.policy import ImagingPolicy
from medpolicy.policy.evaluator import evaluate_case


TEST_DATE = date(2026, 8, 15)


def build_policy() -> ImagingPolicy:
    return ImagingPolicy(
        policy_id="POL-IMG-001",
        version="1.0",
        allowed_diagnosis_codes={
            "SYN-LBP-001",
            "SYN-RAD-001",
        },
        minimum_conservative_treatment_weeks=6,
        duplicate_imaging_window_days=90,
    )


def build_valid_case() -> PriorAuthCase:
    return PriorAuthCase(
        case_id="CASE-001",
        patient_id="PATIENT-001",
        requested_service_code="SYN-IMG-MRI",
        coverage=CoverageInfo(
            payer_id="SYNTHETIC-PAYER",
            member_id="MEMBER-001",
            active=True,
        ),
        diagnoses=[
            Diagnosis(
                code="SYN-LBP-001",
                display="Synthetic diagnosis",
            )
        ],
        treatments=[
            ConservativeTreatment(
                treatment_type="physical_therapy",
                duration_weeks=8,
                completed=True,
            )
        ],
        symptoms_persist=True,
        prior_imaging=[],
    )


def test_valid_case_is_approved():
    policy = build_policy()
    case = build_valid_case()

    decision = evaluate_case(
        case=case,
        policy=policy,
        today=TEST_DATE,
    )

    assert decision.status == DecisionStatus.APPROVE


def test_inactive_coverage_is_denied():
    policy = build_policy()
    case = build_valid_case()

    case.coverage.active = False

    decision = evaluate_case(
        case=case,
        policy=policy,
        today=TEST_DATE,
    )

    assert decision.status == DecisionStatus.DENY


def test_missing_treatment_is_pended():
    policy = build_policy()
    case = build_valid_case()

    case.treatments = []

    decision = evaluate_case(
        case=case,
        policy=policy,
        today=TEST_DATE,
    )

    assert decision.status == DecisionStatus.PEND

    treatment_result = next(
        criterion
        for criterion in decision.criteria
        if criterion.criterion_id
        == "conservative_treatment"
    )

    assert (
        treatment_result.status
        == CriterionStatus.UNKNOWN
    )

    assert (
        "conservative_treatment_history"
        in decision.missing_information
    )


def test_insufficient_treatment_is_denied():
    policy = build_policy()
    case = build_valid_case()

    case.treatments = [
        ConservativeTreatment(
            treatment_type="physical_therapy",
            duration_weeks=3,
            completed=True,
        )
    ]

    decision = evaluate_case(
        case=case,
        policy=policy,
        today=TEST_DATE,
    )

    assert decision.status == DecisionStatus.DENY


def test_missing_symptom_status_is_pended():
    policy = build_policy()
    case = build_valid_case()

    case.symptoms_persist = None

    decision = evaluate_case(
        case=case,
        policy=policy,
        today=TEST_DATE,
    )

    assert decision.status == DecisionStatus.PEND

    assert (
        "symptom_persistence"
        in decision.missing_information
    )


def test_recent_duplicate_imaging_is_denied():
    policy = build_policy()
    case = build_valid_case()

    case.prior_imaging = [
        PriorImaging(
            service_code="SYN-IMG-MRI",
            performed_date=date(2026, 7, 20),
        )
    ]

    decision = evaluate_case(
        case=case,
        policy=policy,
        today=TEST_DATE,
    )

    assert decision.status == DecisionStatus.DENY


def test_old_imaging_does_not_block_authorization():
    policy = build_policy()
    case = build_valid_case()

    case.prior_imaging = [
        PriorImaging(
            service_code="SYN-IMG-MRI",
            performed_date=date(2025, 1, 1),
        )
    ]

    decision = evaluate_case(
        case=case,
        policy=policy,
        today=TEST_DATE,
    )

    assert decision.status == DecisionStatus.APPROVE