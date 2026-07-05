from dataclasses import dataclass, field


@dataclass(slots=True)
class JobPosting:
    """
    Represents one normalized job posting regardless of source.
    """

    title: str
    company: str
    location: str

    source: str
    url: str

    description: str = ""
    salary: str = ""

    remote: bool = False
    posted_date: str = ""

    # AI-generated metadata
    skills: list[str] = field(default_factory=list)
    seniority: str = ""
    role_category: str = ""
    industry: str = ""