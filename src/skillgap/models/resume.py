from dataclasses import dataclass, field


@dataclass(slots=True)
class ResumeProfile:
    """
    Structured representation of a user's resume.
    """

    name: str = ""
    email: str = ""
    phone: str = ""
    summary: str = ""

    education: list[dict] = field(default_factory=list)
    experience: list[dict] = field(default_factory=list)
    projects: list[dict] = field(default_factory=list)

    skills: dict = field(default_factory=dict)

    certifications: list[str] = field(default_factory=list)
    awards: list[str] = field(default_factory=list)
    organizations: list[dict] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)