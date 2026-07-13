"""
File-related routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..db.database import get_db
from ..models import Repository as RepoModel
from ..schemas.responses import FileNode, FileContent, FileDiff
from ..services.git_service import git_service

router = APIRouter()


@router.get("/repositories/{repo_id}/files", response_model=list[FileNode])
async def get_file_tree(
    repo_id: str,
    commit: Optional[str] = Query('HEAD', description="Commit hash or reference"),
    path: Optional[str] = Query('', description="Subdirectory path"),
    db: AsyncSession = Depends(get_db),
):
    """Get file tree at a specific commit."""
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
    
    # Get file tree
    try:
        nodes = await git_service.get_file_tree(repo, commit, path)
        return nodes
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error getting file tree: {str(e)}")


@router.get("/repositories/{repo_id}/files/{file_path:path}")
async def get_file_content(
    repo_id: str,
    file_path: str,
    commit: Optional[str] = Query('HEAD', description="Commit hash or reference"),
    db: AsyncSession = Depends(get_db),
):
    """Get file content at a specific commit."""
    from sqlalchemy import select
    from urllib.parse import unquote
    
    # Decode URL-encoded path
    file_path = unquote(file_path)
    
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
    
    # Get file content
    try:
        content = await git_service.get_file_content(repo, file_path, commit)
        if not content:
            raise HTTPException(status_code=404, detail="File not found")
        return content
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error getting file content: {str(e)}")


@router.get("/repositories/{repo_id}/files/{file_path:path}/diff")
async def get_file_diff(
    repo_id: str,
    file_path: str,
    from_commit: str = Query(..., description="Source commit hash"),
    to_commit: str = Query(..., description="Target commit hash"),
    db: AsyncSession = Depends(get_db),
):
    """Get diff for a file between two commits."""
    from sqlalchemy import select
    from urllib.parse import unquote
    
    # Decode URL-encoded path
    file_path = unquote(file_path)
    
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
    
    # Get file diffs between commits
    try:
        # Get diff for the entire commit first
        commit_diffs = await git_service.get_commit_diff(repo, to_commit)
        
        # Find the specific file
        file_diff = None
        for diff in commit_diffs:
            if diff.path == file_path or diff.old_path == file_path:
                file_diff = diff
                break
        
        if not file_diff:
            return {"path": file_path, "hunks": [], "insertions": 0, "deletions": 0}
        
        return file_diff
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error getting file diff: {str(e)}")
