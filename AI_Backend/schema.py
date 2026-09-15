from typing import Optional

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    age: Optional[int] = Field(
        default=None,
        description="Age of the user in years."
    )

    income: Optional[int] = Field(
        default=None,
        description="Annual income of the user in Indian Rupees."
    )

    occupation: Optional[str] = Field(
        default=None,
        description="Current occupation of the user."
    )

    state: Optional[str] = Field(
        default=None,
        description="Indian state where the user lives."
    )

    gender: Optional[str] = Field(
        default=None,
        description="Gender of the user: male, female, or other."
    )

    category: Optional[str] = Field(
        default=None,
        description="Social category: General, OBC, SC, ST, or EWS."
    )