from pydantic import BaseModel, Field


class LinkedInSectionAvailability(BaseModel):
    """
    Describes whether a LinkedIn section was actually
    available from the acquisition provider.

    This prevents CareerOS from confusing:

        provider did not return data

    with:

        candidate has no data.
    """

    available: bool

    item_count: int = Field(
        ge=0
    )

    source: str

    note: str | None = None


class LinkedInAcquisitionMetadata(BaseModel):
    """
    Metadata describing what the acquisition provider
    actually returned.
    """

    provider: str

    profile_url: str

    sections: dict[
        str,
        LinkedInSectionAvailability
    ] = Field(
        default_factory=dict
    )