"""
ChronoGit Database Models
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Float, Boolean, Index, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from typing import Optional, Dict, Any, List

Base = declarative_base()


class Repository(Base):
    """Repository metadata and configuration."""
    
    __tablename__ = "repositories"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, unique=True, nullable=False)
    remote_url = Column(String, nullable=True)
    head_commit = Column(String, nullable=True)
    current_branch = Column(String, nullable=True)
    
    # Stats
    total_commits = Column(Integer, default=0)
    total_files = Column(Integer, default=0)
    size_bytes = Column(Integer, default=0)
    
    # Status
    status = Column(String, default="pending")  # pending, indexing, ready, error
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_indexed_at = Column(DateTime, nullable=True)
    last_opened_at = Column(DateTime, nullable=True)
    
    # Configuration (stored as JSON)
    config = Column(JSON, default=dict)
    
    # Relationships
    commits = relationship("Commit", back_populates="repository", cascade="all, delete-orphan")
    branches = relationship("Branch", back_populates="repository", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="repository", cascade="all, delete-orphan")
    authors = relationship("Author", back_populates="repository", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_repositories_name", "name"),
        Index("ix_repositories_status", "status"),
    )


class Author(Base):
    """Commit author/contributor information."""
    
    __tablename__ = "authors"
    
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    
    # Aggregated stats
    commit_count = Column(Integer, default=0)
    total_insertions = Column(Integer, default=0)
    total_deletions = Column(Integer, default=0)
    first_commit_date = Column(DateTime, nullable=True)
    last_commit_date = Column(DateTime, nullable=True)
    
    # Relationships
    repository = relationship("Repository", back_populates="authors")
    commits = relationship("Commit", back_populates="author")
    
    __table_args__ = (
        Index("ix_authors_repository", "repository_id"),
        Index("ix_authors_email", "email"),
    )


class Commit(Base):
    """Git commit information."""
    
    __tablename__ = "commits"
    
    id = Column(String, primary_key=True)  # Full commit hash
    short_hash = Column(String, nullable=False, index=True)
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    
    # Commit details
    message = Column(Text, nullable=False)
    body = Column(Text, nullable=True)
    author_id = Column(String, ForeignKey("authors.id"), nullable=False)
    committer_name = Column(String, nullable=True)
    committer_email = Column(String, nullable=True)
    
    # Timestamp
    committed_at = Column(DateTime, nullable=False, index=True)
    
    # Parent commits (for graph traversal)
    parent_hashes = Column(JSON, default=list)  # Array of parent commit hashes
    
    # Stats
    insertions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    files_changed = Column(Integer, default=0)
    is_merge = Column(Boolean, default=False)
    
    # AI-generated summary
    ai_summary = Column(JSON, nullable=True)
    ai_architecture = Column(JSON, nullable=True)
    
    # Relationships
    repository = relationship("Repository", back_populates="commits")
    author = relationship("Author", back_populates="commits")
    branch_commits = relationship("BranchCommit", back_populates="commit")
    file_changes = relationship("FileChange", back_populates="commit", cascade="all, delete-orphan")
    functions = relationship("FunctionSnapshot", back_populates="commit", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_commits_repo_date", "repository_id", "committed_at"),
        Index("ix_commits_short_hash", "short_hash"),
    )


class Branch(Base):
    """Git branch information."""
    
    __tablename__ = "branches"
    
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    name = Column(String, nullable=False)
    is_remote = Column(Boolean, default=False)
    is_current = Column(Boolean, default=False)
    head_commit = Column(String, nullable=True)
    upstream = Column(String, nullable=True)
    
    # Relationships
    repository = relationship("Repository", back_populates="branches")
    commits = relationship("BranchCommit", back_populates="branch", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_branches_repository", "repository_id"),
        Index("ix_branches_name", "name"),
    )


class BranchCommit(Base):
    """Association table for branch-commit relationships."""
    
    __tablename__ = "branch_commits"
    
    id = Column(String, primary_key=True)
    branch_id = Column(String, ForeignKey("branches.id"), nullable=False)
    commit_id = Column(String, ForeignKey("commits.id"), nullable=False)
    position = Column(Integer, nullable=True)  # Position in branch history
    
    # Relationships
    branch = relationship("Branch", back_populates="commits")
    commit = relationship("Commit", back_populates="branch_commits")
    
    __table_args__ = (
        Index("ix_branch_commits_branch", "branch_id"),
        Index("ix_branch_commits_commit", "commit_id"),
    )


class Tag(Base):
    """Git tag information."""
    
    __tablename__ = "tags"
    
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    name = Column(String, nullable=False)
    commit_hash = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    tagger_name = Column(String, nullable=True)
    tagger_email = Column(String, nullable=True)
    tagged_at = Column(DateTime, nullable=True)
    
    # Relationships
    repository = relationship("Repository", back_populates="tags")
    
    __table_args__ = (
        Index("ix_tags_repository", "repository_id"),
        Index("ix_tags_name", "name"),
        Index("ix_tags_commit", "commit_hash"),
    )


class FileChange(Base):
    """File changes in a commit."""
    
    __tablename__ = "file_changes"
    
    id = Column(String, primary_key=True)
    commit_id = Column(String, ForeignKey("commits.id"), nullable=False)
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    
    # File info
    path = Column(String, nullable=False)
    old_path = Column(String, nullable=True)  # For renamed files
    status = Column(String, nullable=False)  # added, modified, deleted, renamed, copied
    
    # Change stats
    insertions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    size_before = Column(Integer, nullable=True)
    size_after = Column(Integer, nullable=True)
    
    # Diff data (can be large, stored separately or compressed)
    diff_data = Column(JSON, nullable=True)
    
    # Language detection
    language = Column(String, nullable=True)
    
    # Relationships
    commit = relationship("Commit", back_populates="file_changes")
    repository = relationship("Repository")
    
    __table_args__ = (
        Index("ix_file_changes_commit", "commit_id"),
        Index("ix_file_changes_repository", "repository_id"),
        Index("ix_file_changes_path", "path"),
    )


class FunctionSnapshot(Base):
    """Function/method snapshot at a specific commit."""
    
    __tablename__ = "function_snapshots"
    
    id = Column(String, primary_key=True)
    commit_id = Column(String, ForeignKey("commits.id"), nullable=False)
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    
    # Function info
    name = Column(String, nullable=False)
    kind = Column(String, nullable=False)  # function, class, method, interface, etc.
    signature = Column(Text, nullable=False)
    file_path = Column(String, nullable=False)
    
    # Location
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    
    # Metadata
    parameters = Column(JSON, nullable=True)
    return_type = Column(String, nullable=True)
    access_modifier = Column(String, nullable=True)
    is_static = Column(Boolean, default=False)
    is_async = Column(Boolean, default=False)
    doc_comment = Column(Text, nullable=True)
    complexity = Column(Integer, nullable=True)
    
    # Hash for change detection
    content_hash = Column(String, nullable=True)
    
    # Relationships
    commit = relationship("Commit", back_populates="functions")
    repository = relationship("Repository")
    
    __table_args__ = (
        Index("ix_functions_commit", "commit_id"),
        Index("ix_functions_repository", "repository_id"),
        Index("ix_functions_name", "name"),
        Index("ix_functions_file", "file_path"),
    )


class HeatmapEntry(Base):
    """Heatmap data for visualization."""
    
    __tablename__ = "heatmap_entries"
    
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    
    # Path being tracked
    path = Column(String, nullable=False)
    path_type = Column(String, nullable=False)  # file, directory, function
    
    # Metrics
    modification_count = Column(Integer, default=0)
    total_insertions = Column(Integer, default=0)
    total_deletions = Column(Integer, default=0)
    unique_authors = Column(Integer, default=0)
    avg_complexity = Column(Float, nullable=True)
    
    # Time-based tracking
    first_modified = Column(DateTime, nullable=True)
    last_modified = Column(DateTime, nullable=True)
    
    # Relationships
    repository = relationship("Repository")
    
    __table_args__ = (
        Index("ix_heatmap_repository", "repository_id"),
        Index("ix_heatmap_path", "path"),
    )


class SearchIndex(Base):
    """Full-text search index."""
    
    __tablename__ = "search_index"
    
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    
    # Indexed content
    item_type = Column(String, nullable=False)  # commit, file, function, author
    item_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    path = Column(String, nullable=True)
    commit_hash = Column(String, nullable=True)
    
    # Metadata for filtering
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    repository = relationship("Repository")
    
    __table_args__ = (
        Index("ix_search_repository", "repository_id"),
        Index("ix_search_type", "item_type"),
        Index("ix_search_title", "title"),
    )


class ReplayState(Base):
    """Stored replay state for sessions."""
    
    __tablename__ = "replay_states"
    
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    session_id = Column(String, nullable=True)
    
    # State
    current_commit = Column(String, nullable=False)
    is_playing = Column(Boolean, default=False)
    speed = Column(Integer, default=500)
    direction = Column(String, default="forward")
    skip_merges = Column(Boolean, default=False)
    start_commit = Column(String, nullable=True)
    end_commit = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository")
    
    __table_args__ = (
        Index("ix_replay_repository", "repository_id"),
        Index("ix_replay_session", "session_id"),
    )
