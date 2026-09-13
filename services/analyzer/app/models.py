from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class RepositorySummary(BaseModel):
    full_name: str | None = None
    description: str | None = None
    default_branch: str | None = None
    visibility: str | None = None
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    size_kb: int = 0
    languages: dict[str, float] = Field(default_factory=dict)
    updated_at: str | None = None


class StructureAnalysis(BaseModel):
    repository: str
    file_count: int
    directory_count: int
    files: list[str]
    directories: list[str]
    framework_signals: list[str]
    quality_signals: list[str]


class DeepStructureAnalysis(BaseModel):
    repository: str
    ref: str
    file_count: int
    directory_count: int
    max_depth: int
    framework_signals: list[str]
    quality_signals: list[str]
    truncated: bool


class EngineeringHealth(BaseModel):
    score: int = Field(ge=0, le=100)
    grade: str
    recommendations: list[str]


class RepositoryOverview(BaseModel):
    repository: str
    summary: RepositorySummary
    structure: StructureAnalysis
    engineering_health: EngineeringHealth


class CommitActivity(BaseModel):
    repository: str
    ref: str | None = None
    requested_limit: int = Field(ge=1, le=100)
    commit_count: int = Field(ge=0)
    unique_author_count: int = Field(ge=0)
    merge_commit_count: int = Field(ge=0)
    newest_commit_at: str | None = None
    oldest_commit_at: str | None = None
