from medpolicy.domain.case import PriorAuthCase
from medpolicy.domain.policy import ImagingPolicy
from medpolicy.domain.decision import (
    CriterionResult,
    CriterionStatus,
    Decision,
    DecisionStatus,
)

from datetime import date



def evaluate_case(
    case: PriorAuthCase,
    policy: ImagingPolicy,
    today: date,
) -> Decision:
 
    criteria: list[CriterionResult] = []
    missing_information: list[str] = []

    # Criterion 1: Coverage
    coverage_status = (
        CriterionStatus.MET
        if case.coverage.active
        else CriterionStatus.NOT_MET
    )
    criteria.append(
        CriterionResult(
            criterion_id="coverage_active",
            description="Patient coverage must be active.",
            status=coverage_status,
            evidence=[
                f"coverage:{case.coverage.member_id}"
            ],
        )
    )
        # Criterion 2: Qualifying diagnosis
    diagnosis_matches = [
        diagnosis
        for diagnosis in case.diagnoses
        if diagnosis.code in policy.allowed_diagnosis_codes
    ]

    diagnosis_status = (
        CriterionStatus.MET
        if diagnosis_matches
        else CriterionStatus.NOT_MET
    )

    criteria.append(
        CriterionResult(
            criterion_id="qualifying_diagnosis",
            description="A qualifying diagnosis must be documented.",
            status=diagnosis_status,
            evidence=[
                f"diagnosis:{diagnosis.code}"
                for diagnosis in diagnosis_matches
            ],
        )
    )
    # Criterion 3: Conservative treatment
    if not case.treatments:
        treatment_status = CriterionStatus.UNKNOWN
        missing_information.append("conservative_treatment_history")
        treatment_evidence = []
    else:
        qualifying_treatments = [
            treatment
            for treatment in case.treatments
            if treatment.completed
            and treatment.duration_weeks
            >= policy.minimum_conservative_treatment_weeks
        ]

        treatment_status = (
            CriterionStatus.MET
            if qualifying_treatments
            else CriterionStatus.NOT_MET
        )

        treatment_evidence = [
            (
                f"treatment:{treatment.treatment_type}:"
                f"{treatment.duration_weeks}_weeks"
            )
            for treatment in qualifying_treatments
        ]

    criteria.append(
        CriterionResult(
            criterion_id="conservative_treatment",
            description=(
                "Required conservative treatment duration must be completed."
            ),
            status=treatment_status,
            evidence=treatment_evidence,
        )
    )
        # Criterion 4: Symptoms must still persist.

    if case.symptoms_persist is None:
        symptoms_status = CriterionStatus.UNKNOWN
        missing_information.append("symptom_persistence")
        symptoms_evidence = []

    elif case.symptoms_persist:
        symptoms_status = CriterionStatus.MET
        symptoms_evidence = ["symptoms:persistent"]

    else:
        symptoms_status = CriterionStatus.NOT_MET
        symptoms_evidence = ["symptoms:not_persistent"]

    criteria.append(
        CriterionResult(
            criterion_id="persistent_symptoms",
            description=(
                "Symptoms must persist after conservative treatment."
            ),
            status=symptoms_status,
            evidence=symptoms_evidence,
        )
    )
        # Criterion 5: No duplicate imaging within the policy window.

    if case.prior_imaging is None:

        duplicate_status = CriterionStatus.UNKNOWN

        missing_information.append(
            "prior_imaging_history"
        )

        duplicate_evidence = []

    else:

        recent_duplicate_imaging = []

        for imaging in case.prior_imaging:

            if imaging.service_code != case.requested_service_code:
                continue

            age_days = (
                today - imaging.performed_date
            ).days

            if (
                0
                <= age_days
                <= policy.duplicate_imaging_window_days
            ):
                recent_duplicate_imaging.append(imaging)

        duplicate_status = (
            CriterionStatus.NOT_MET
            if recent_duplicate_imaging
            else CriterionStatus.MET
        )

        duplicate_evidence = [
            (
                f"prior_imaging:"
                f"{imaging.service_code}:"
                f"{imaging.performed_date.isoformat()}"
            )
            for imaging in recent_duplicate_imaging
        ]

    criteria.append(
        CriterionResult(
            criterion_id="duplicate_imaging",
            description=(
                "No duplicate advanced imaging may exist "
                "within the policy window."
            ),
            status=duplicate_status,
            evidence=duplicate_evidence,
        )
    )


    statuses = {
        result.status
        for result in criteria
    }

    if case.treatments is None:

        treatment_status = CriterionStatus.UNKNOWN

        missing_information.append(
            "conservative_treatment_history"
        )

        treatment_evidence = []

    else:

        qualifying_treatments = [
            treatment
            for treatment in case.treatments
            if treatment.completed
            and treatment.duration_weeks
            >= policy.minimum_conservative_treatment_weeks
        ]

        treatment_status = (
            CriterionStatus.MET
            if qualifying_treatments
            else CriterionStatus.NOT_MET
        )

        treatment_evidence = [
            (
                f"treatment:{treatment.treatment_type}:"
                f"{treatment.duration_weeks}_weeks"
            )
            for treatment in qualifying_treatments
        ]