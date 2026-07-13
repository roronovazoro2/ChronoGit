"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# ============================================================================
# Author Schemas
# ============================================================================

class AuthorBase(BaseModel):
    name: str
    email: str


class AuthorCreate(AuthorBase):
    repository_id: str


class AuthorResponse(AuthorBase):
    id: str
    repository_id: str
    commit_count: int = 0
    total_insertions: int = 0
    total_deletions: int = 0
    first_commit_date: Optional[datetime] = None
    last_commit_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Commit Schemas
# ============================================================================

class CommitBase(BaseModel):
    message: str
    body: Optional[str] = None
    author_name: str
    author_email: str
    committed_at: datetime
    insertions: int = 0
    deletions: int = 0
    files_changed: int = 0
    is_merge: bool = False


class CommitCreate(CommitBase):
    id: str
    short_hash: str
    repository_id: str
    author_id: str
    parent_hashes: List[str] = []


class AISummary(BaseModel):
    title: str
    description: str
    changes: List[str]
    impact: str
    confidence: float
    model: str
    generated_at: datetime


class CommitResponse(CommitBase):
    id: str
    short_hash: str
    repository_id: str
    author_id: str
    author: Optional[AuthorResponse] = None
    parent_hashes: List[str] = []
    ai_summary: Optional[Dict[str, Any]] = None
    branches: List[str] = []
    tags: List[str] = []
    
    class Config:
        from_attributes = True


class CommitListResponse(BaseModel):
    commits: List[CommitResponse]
    total: int
    has_more: bool


# ============================================================================
# Repository Schemas
# ============================================================================

class RepositoryConfig(BaseModel):
    max_commits_to_index: Optional[int] = None
    enable_ai: bool = True
    enable_parsing: bool = True
    excluded_paths: List[str] = []
    included_languages: List[str] = []


class RepositoryBase(BaseModel):
    name: str
    path: str
    remote_url: Optional[str] = None
    config: Optional[RepositoryConfig] = None


class RepositoryCreate(RepositoryBase):
    pass


class RepositoryUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[RepositoryConfig] = None


class RepositoryStats(BaseModel):
    total_commits: int
    total_files: int
    total_directories: int
    total_lines: int
    first_commit: datetime
    last_commit: datetime
    age_days: int
    contributors: int
    branches: int
    tags: int
    average_commit_size: float


class RepositoryResponse(RepositoryBase):
    id: str
    head_commit: Optional[str] = None
    current_branch: Optional[str] = None
    total_commits: int = 0
    total_files: int = 0
    size_bytes: int = 0
    status: str = "pending"
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_indexed_at: Optional[datetime] = None
    last_opened_at: Optional[datetime] = None
    stats: Optional[RepositoryStats] = None
    
    class Config:
        from_attributes = True


class RepositoryImportRequest(BaseModel):
    path: str
    name: Optional[str] = None
    config: Optional[RepositoryConfig] = None


# ============================================================================
# File Schemas
# ============================================================================

class FileNode(BaseModel):
    id: str
    name: str
    path: str
    type: str  # 'file' or 'directory'
    size: Optional[int] = None
    children: Optional[List['FileNode']] = None
    status: Optional[str] = None
    language: Optional[str] = None
    icon: Optional[str] = None


class FileContent(BaseModel):
    path: str
    content: str
    encoding: str = "utf-8"
    size: int
    language: str
    lines: int
    sha: str


class DiffLine(BaseModel):
    type: str  # 'context', 'add', 'delete'
    content: str
    line_number: Optional[int] = None
    old_line_number: Optional[int] = None
    new_line_number: Optional[int] = None


class DiffHunk(BaseModel):
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    header: str
    lines: List[DiffLine]


class FileDiff(BaseModel):
    path: str
    old_path: Optional[str] = None
    status: str
    hunks: List[DiffHunk]
    insertions: int
    deletions: int
    binary: bool = False


class FileChangeResponse(BaseModel):
    path: str
    old_path: Optional[str] = None
    status: str
    insertions: int
    deletions: int
    language: Optional[str] = None
    diff: Optional[FileDiff] = None


# ============================================================================
# Branch & Tag Schemas
# ============================================================================

class BranchResponse(BaseModel):
    name: str
    is_current: bool
    is_remote: bool
    head_commit: str
    upstream: Optional[str] = None
    
    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    name: str
    commit: str
    message: Optional[str] = None
    tagger_name: Optional[str] = None
    tagger_email: Optional[str] = None
    tagged_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Function Analysis Schemas
# ============================================================================

class ParameterInfo(BaseModel):
    name: str
    type: Optional[str] = None
    optional: bool = False
    default_value: Optional[str] = None


class FunctionInfo(BaseModel):
    name: str
    kind: str  # 'function', 'class', 'method', etc.
    signature: str
    file_path: str
    start_line: int
    end_line: int
    parameters: Optional[List[ParameterInfo]] = None
    return_type: Optional[str] = None
    access_modifier: Optional[str] = None
    is_static: bool = False
    is_async: bool = False
    doc_comment: Optional[str] = None
    complexity: Optional[int] = None


class FunctionDiff(BaseModel):
    name: str
    kind: str
    status: str  # 'added', 'removed', 'modified', 'renamed', 'moved'
    old_signature: Optional[str] = None
    new_signature: Optional[str] = None
    file_path: Optional[str] = None
    old_file_path: Optional[str] = None


# ============================================================================
# Analytics Schemas
# ============================================================================

class ContributorStats(BaseModel):
    author: AuthorResponse
    commits: int
    insertions: int
    deletions: int
    first_commit: datetime
    last_commit: datetime
    active_days: int
    languages: Dict[str, int]
    average_commit_size: float


class HeatmapEntry(BaseModel):
    path: str
    path_type: str
    value: float
    metrics: Dict[str, Any]


class HeatmapResponse(BaseModel):
    type: str
    data: List[HeatmapEntry]
    max: float
    min: float


class LanguageStats(BaseModel):
    name: str
    files: int
    lines: int
    percentage: float
    color: str


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float
    label: Optional[str] = None


# ============================================================================
# Search Schemas
# ============================================================================

class Highlight(BaseModel):
    text: str
    matched: bool


class SearchResult(BaseModel):
    type: str  # 'commit', 'file', 'function', 'author', 'branch', 'tag'
    id: str
    title: str
    subtitle: Optional[str] = None
    path: Optional[str] = None
    commit: Optional[str] = None
    score: float
    highlights: Optional[List[Highlight]] = None


class SearchQuery(BaseModel):
    query: str
    types: List[str] = []
    commit_range: Optional[tuple[str, str]] = None
    authors: Optional[List[str]] = None
    files: Optional[List[str]] = None
    limit: int = 50
    offset: int = 0


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str


# ============================================================================
# AI Schemas
# ============================================================================

class BugAnalysisRequest(BaseModel):
    description: str
    commit_hash: Optional[str] = None
    function_name: Optional[str] = None
    file_path: Optional[str] = None


class EvidenceItem(BaseModel):
    type: str
    description: str
    relevance: float
    location: Optional[Dict[str, Any]] = None


class BugAnalysisResponse(BaseModel):
    likely_commit: str
    probability: float
    reasoning: str
    affected_files: List[str]
    related_commits: List[str]
    suggested_fix: Optional[str] = None
    evidence: List[EvidenceItem]


class ArchitectureExplanation(BaseModel):
    overview: str
    components: List[Dict[str, Any]]
    dependencies: List[Dict[str, Any]]
    patterns: List[str]
    suggestions: List[str]


# ============================================================================
# Graph Schemas
# ============================================================================

class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    size: Optional[float] = None
    color: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str
    weight: Optional[float] = None
    label: Optional[str] = None


class GraphCluster(BaseModel):
    id: str
    label: str
    nodes: List[str]
    color: Optional[str] = None


class DependencyGraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    clusters: List[GraphCluster]


# ============================================================================
# Replay Schemas
# ============================================================================

class ReplayControl(BaseModel):
    action: str  # 'play', 'pause', 'stop', 'next', 'prev', 'jump'
    speed: Optional[int] = None
    commit_hash: Optional[str] = None
    skip_merges: Optional[bool] = None
    direction: Optional[str] = None


class ReplayState(BaseModel):
    is_playing: bool
    current_commit: str
    speed: int
    direction: str
    skip_merges: bool
    start_commit: Optional[str]
    end_commit: Optional[str]
    progress: float


# ============================================================================
# Timeline Schemas
# ============================================================================

class TimelineNode(BaseModel):
    id: str
    commit: CommitResponse
    x: float
    y: float
    z: Optional[float] = None
    cluster: Optional[str] = None
    color: str
    size: float


class TimelineEdge(BaseModel):
    source: str
    target: str
    type: str


class TimelineResponse(BaseModel):
    nodes: List[TimelineNode]
    edges: List[TimelineEdge]
    clusters: List[GraphCluster]
    metadata: Dict[str, Any]


# ============================================================================
# Generic Response Schemas
# ============================================================================

class APIError(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class APIResponse(BaseModel):
    data: Optional[Any] = None
    meta: Optional[Dict[str, Any]] = None
    error: Optional[APIError] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    pagination: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    version: str
    database: bool
    git_available: bool
