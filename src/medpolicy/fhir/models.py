from typing import Annotated, Literal, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

class FHIRBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="ignore"
    )

class FHIRIdentifier(FHIRBaseModel):
    system: str | None = None
    value: str


class FHIRReference(FHIRBaseModel):
    reference: str | None = None
    display: str | None = None


class FHIRCoding(FHIRBaseModel):
    system: str | None = None
    code: str
    display: str | None = None


class FHIRCodeableConcept(FHIRBaseModel):
    coding: list[FHIRCoding] = Field(
        default_factory=list
    )

    text: str | None = None



class FHIRCoverage(FHIRBaseModel):
    resourceType: Literal["Coverage"]

    id: str

    status: Literal[
        "active",
        "cancelled",
        "draft",
        "entered-in-error",
    ]

    identifier: list[FHIRIdentifier] = Field(
        default_factory=list
    )

    subscriberId: str | None = None

    beneficiary: FHIRReference

    payor: list[FHIRReference] = Field(
        min_length=1
    )

class FHIRCondition(FHIRBaseModel):
    resourceType: Literal["Condition"]


    id: str


    subject: FHIRReference


    code: FHIRCodeableConcept | None = None

class FHIRServiceRequest(FHIRBaseModel):
    resourceType: Literal["ServiceRequest"]

    id: str

    status: Literal[
        "draft",
        "active",
        "on-hold",
        "revoked",
        "completed",
        "entered-in-error",
        "unknown",
    ]

    intent: Literal[
        "proposal",
        "plan",
        "directive",
        "order",
        "original-order",
        "reflex-order",
        "filler-order",
        "instance-order",
        "option",
    ]

    subject: FHIRReference

    code: FHIRCodeableConcept | None = None

    FHIRResource = Annotated[
    Union[
        FHIRPatient,
        FHIRCoverage,
        FHIRCondition,
        FHIRServiceRequest,
    ],
    Field(discriminator="resourceType"),
]