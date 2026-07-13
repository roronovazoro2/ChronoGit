"""
Commit-related routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from ..db.database import get_db
from ..models import Repository as RepoModel, Commit as CommitModel, Author
from ..schemas.responses import CommitResponse, CommitListResponse
from ..services.git_service import git_service

router = APIRouter()


@router.get("/repositories/{repo_id}/commits", response_model=CommitListResponse)
async def list_commits(
    repo_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    branch: Optional[str] = None,
    author: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
):
    """List commits for a repository with pagination."""
    from sqlalchemy import select, func
    
    # Verify repository exists
    result = await db.execute(select(RepoModel).where(RepoModel.id == repo_id))
    repository = result.scalar_one_or_none()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Open Git repository
    try:
        repo = await git_service.open_repository(repository.path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Get commits from Git (with basic filtering)
    offset = (page - 1) * page_size
    
    try:
        # Iterate commits with skip/limit
        all_commits = []
        skip = 0
        
        for batch in await git_service.iterate_commits(repo, batch_size=page_size * 2):
            for commit in batch:
                if skip < offset:
                    skip += 1
                    continue
                
                # Apply filters
                if author and commit.author.email != author:
                    continue
                if since and datetime.fromtimestamp(commit.committed_date) < since:
                    continue
                if until and datetime.fromtimestamp(commit.committed_date) > until:
                    continue
                
                all_commits.append(commit)
                
                if len(all_commits) >= page_size:
                    break
            
            if len(all_commits) >= page_size:
                break
        
        # Convert to response format
        commits_response = []
        for commit in all_commits:
            details = await git_service.get_commit_details(repo, commit.hexsha)
            
            # Get or create author
            author_result = await db.execute(
                select(Author).where(
                    Author.repository_id == repo_id,
                    Author.email == details['author_email']
                )
            )
            author = author_result.scalar_one_or_none()
            
            if not author:
                author = Author(
                    id=f"{repo_id}_{details['author_email'].replace('@', '_at_')}",
                    repository_id=repo_id,
                    name=details['author_name'],
                    email=details['author_email'],
                )
                db.add(author)
            
            commit_response = CommitResponse(
                id=details['hash'],
                short_hash=details['short_hash'],
                repository_id=repo_id,
                author_id=author.id,
                author=author,
                message=details['message'],
                body=details['body'],
                committed_at=details['committed_at'],
                insertions=details['insertions'],
                deletions=details['deletions'],
                files_changed=details['files_changed'],
                is_merge=details['is_merge'],
                parent_hashes=details['parents'],
                branches=details['branches'],
                tags=details['tags'],
            )
            commits_response.append(commit_response)
        
        await db.commit()
        
        # Check if there are more commits
        has_more = len(all_commits) == page_size
        
        return CommitListResponse(
            commits=commits_response,
            total=len(commits_response),
            has_more=has_more,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching commits: {str(e)}")


@router.get("/repositories/{repo_id}/commits/{commit_hash}", response_model=CommitResponse)
async def get_commit(
    repo_id: str,
    commit_hash: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific commit."""
    from sqlalchemy import select
    
    # Verify repository exists
    result = await db.execute(select(RepoModel).where(RepoModel.id == repo_id))
    repository = result.scalar_one_or_none()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Open Git repository
    try:
        repo = await git_service.open_repository(repository.path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Get commit details
    try:
        details = await git_service.get_commit_details(repo, commit_hash)
    except Exception:
        raise HTTPException(status_code=404, detail="Commit not found")
    
    # Get or create author
    author_result = await db.execute(
        select(Author).where(
            Author.repository_id == repo_id,
            Author.email = details['author_email']
        )
    )
    author = author_result.scalar_one_or_none()
    
    if not author:
        author = Author(
            id=f"{repo_id}_{details['author_email'].replace('@', '_at_')}",
            repository_id=repo_id,
            name=details['author_name'],
            email=details['author_email'],
        )
        db.add(author)
        await db.commit()
    
    return CommitResponse(
        id=details['hash'],
        short_hash=details['short_hash'],
        repository_id=repo_id,
        author_id=author.id,
        author=author,
        message=details['message'],
        body=details['body'],
        committed_at=details['committed_at'],
        insertions=details['insertions'],
        deletions=details['deletions'],
        files_changed=details['files_changed'],
        is_merge=details['is_merge'],
        parent_hashes=details['parents'],
        branches=details['branches'],
        tags=details['tags'],
    )


@router.get("/repositories/{repo_id}/commits/{commit_hash}/diff")
async def get_commit_diff(
    repo_id: str,
    commit_hash: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the diff for a specific commit."""
    from sqlalchemy import select
    
    # Verify repository exists
    result = await db.execute(select(RepoModel).where(RepoModel.id == repo_id))
    repository = result.scalar_one_or_none()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Open Git repository
    try:
        repo = await git_service.open_repository(repository.path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Get diff
    try:
        diffs = await git_service.get_commit_diff(repo, commit_hash)
        return {"commit": commit_hash, "files": diffs}
    except Exception:
        raise HTTPException(status_code=404, detail="Commit not found")
