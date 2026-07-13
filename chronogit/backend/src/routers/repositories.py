"""
Repository management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
import os

from ..db.database import get_db
from ..models import Repository as RepoModel
from ..schemas.responses import (
    RepositoryResponse, RepositoryCreate, RepositoryUpdate,
    RepositoryImportRequest, RepositoryStats
)
from ..services.git_service import git_service

router = APIRouter()


@router.get("", response_model=List[RepositoryResponse])
async def list_repositories(
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = None,
):
    """List all indexed repositories."""
    from sqlalchemy import select
    
    query = select(RepoModel)
    if status_filter:
        query = query.where(RepoModel.status == status_filter)
    
    result = await db.execute(query)
    repositories = result.scalars().all()
    
    return repositories


@router.post("/import", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def import_repository(
    request: RepositoryImportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Import a new Git repository."""
    from sqlalchemy import select
    
    # Validate path
    abs_path = os.path.abspath(request.path)
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=400, detail="Repository path does not exist")
    
    if not os.path.exists(os.path.join(abs_path, '.git')):
        raise HTTPException(status_code=400, detail="Not a Git repository")
    
    # Check if already imported
    result = await db.execute(select(RepoModel).where(RepoModel.path == abs_path))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Repository already imported")
    
    # Open repo and get initial info
    try:
        repo = await git_service.open_repository(abs_path)
        head_commit = await git_service.get_head_commit(repo)
        current_branch = repo.active_branch.name if not repo.head.is_detached else None
        stats = await git_service.get_repository_stats(repo)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Create repository record
    repo_id = str(uuid.uuid4())
    db_repo = RepoModel(
        id=repo_id,
        name=request.name or os.path.basename(abs_path),
        path=abs_path,
        head_commit=head_commit,
        current_branch=current_branch,
        total_commits=stats.get('total_commits', 0),
        total_files=stats.get('total_files', 0),
        status='indexing',
        config=request.config.model_dump() if request.config else {},
    )
    
    db.add(db_repo)
    await db.commit()
    await db.refresh(db_repo)
    
    # Start background indexing (simplified - in production use Celery/Redis Queue)
    # For now, we'll mark as ready and index on-demand
    
    return db_repo


@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get repository details."""
    from sqlalchemy import select
    
    result = await db.execute(select(RepoModel).where(RepoModel.id == repo_id))
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Update last opened
    from datetime import datetime
    repository.last_opened_at = datetime.utcnow()
    await db.commit()
    
    return repository


@router.put("/{repo_id}", response_model=RepositoryResponse)
async def update_repository(
    repo_id: str,
    update_data: RepositoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update repository configuration."""
    from sqlalchemy import select
    
    result = await db.execute(select(RepoModel).where(RepoModel.id == repo_id))
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Update fields
    if update_data.name is not None:
        repository.name = update_data.name
    if update_data.config is not None:
        repository.config = update_data.config.model_dump()
    
    await db.commit()
    await db.refresh(repository)
    
    return repository


@router.delete("/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repository(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a repository from the index."""
    from sqlalchemy import select, delete
    
    result = await db.execute(select(RepoModel).where(RepoModel.id == repo_id))
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Close repo if open
    git_service.close_repository(repository.path)
    
    # Delete from database
    await db.execute(delete(RepoModel).where(RepoModel.id == repo_id))
    await db.commit()


@router.get("/{repo_id}/stats", response_model=RepositoryStats)
async def get_repository_stats(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed repository statistics."""
    from sqlalchemy import select
    from datetime import datetime
    
    result = await db.execute(select(RepoModel).where(RepoModel.id == repo_id))
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Get fresh stats from Git
    try:
        repo = await git_service.open_repository(repository.path)
        stats = await git_service.get_repository_stats(repo)
    except Exception:
        stats = {}
    
    # Calculate additional metrics
    age_days = 0
    if repository.total_commits > 0:
        # Would need commit dates for accurate calculation
        age_days = 365  # Placeholder
    
    avg_commit_size = 0.0
    if repository.total_commits > 0 and repository.total_files > 0:
        avg_commit_size = repository.total_files / max(repository.total_commits, 1)
    
    return RepositoryStats(
        total_commits=repository.total_commits or stats.get('total_commits', 0),
        total_files=repository.total_files or stats.get('total_files', 0),
        total_directories=0,  # Would need to calculate
        total_lines=0,  # Would need to calculate
        first_commit=datetime.now(),  # Placeholder
        last_commit=datetime.now(),  # Placeholder
        age_days=age_days,
        contributors=stats.get('contributors', 0),
        branches=stats.get('total_branches', 0),
        tags=stats.get('total_tags', 0),
        average_commit_size=avg_commit_size,
    )
