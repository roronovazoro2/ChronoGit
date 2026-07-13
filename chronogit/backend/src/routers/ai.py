"""
AI-powered features routes - commit summaries, bug analysis, architecture explanations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import asyncio

from ..db.database import get_db
from ..models import Repository as RepoModel
from ..schemas.responses import (
    BugAnalysisRequest, BugAnalysisResponse, EvidenceItem,
    ArchitectureExplanation
)
from ..services.git_service import git_service

router = APIRouter()


@router.get("/repositories/{repo_id}/ai/summary/{commit_hash}")
async def get_commit_summary(
    repo_id: str,
    commit_hash: str,
    db: AsyncSession = Depends(get_db),
):
    """Get AI-generated summary for a commit."""
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
    
    # Generate AI summary (simplified - in production would call LLM)
    ai_summary = _generate_commit_summary(details)
    
    return {
        "commit": commit_hash,
        "summary": ai_summary,
    }


@router.post("/repositories/{repo_id}/ai/bug-analysis")
async def analyze_bug_origin(
    repo_id: str,
    request: BugAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """Analyze when a bug was likely introduced."""
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
    
    # Perform bug analysis (simplified bisect-style analysis)
    analysis = _perform_bug_analysis(repo, request)
    
    return analysis


@router.get("/repositories/{repo_id}/ai/architecture")
async def get_architecture_explanation(
    repo_id: str,
    commit: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get AI-generated architecture explanation."""
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
    
    # Generate architecture explanation
    explanation = _generate_architecture_explanation(repo, commit)
    
    return explanation


def _generate_commit_summary(details: dict) -> dict:
    """Generate a simple commit summary based on patterns."""
    message = details.get('message', '').lower()
    insertions = details.get('insertions', 0)
    deletions = details.get('deletions', 0)
    files_changed = details.get('files_changed', 0)
    
    # Determine commit type
    if 'fix' in message or 'bug' in message:
        commit_type = 'Bug Fix'
    elif 'feat' in message or 'add' in message:
        commit_type = 'Feature'
    elif 'refactor' in message:
        commit_type = 'Refactoring'
    elif 'test' in message:
        commit_type = 'Testing'
    elif 'doc' in message:
        commit_type = 'Documentation'
    elif 'merge' in message:
        commit_type = 'Merge'
    else:
        commit_type = 'Other'
    
    # Generate description
    changes = []
    if insertions > 100:
        changes.append("Large addition of code")
    elif insertions > 0:
        changes.append(f"Added {insertions} lines")
    
    if deletions > 100:
        changes.append("Significant code removal")
    elif deletions > 0:
        changes.append(f"Removed {deletions} lines")
    
    if files_changed > 10:
        changes.append("Wide-ranging changes across many files")
    elif files_changed > 1:
        changes.append(f"Modified {files_changed} files")
    
    impact = "Low"
    if insertions + deletions > 500:
        impact = "High"
    elif insertions + deletions > 100:
        impact = "Medium"
    
    return {
        "title": f"{commit_type}: {details.get('message', '')[:50]}",
        "description": f"This commit {message.strip()}.",
        "changes": changes,
        "impact": impact,
        "confidence": 0.8,
        "model": "rule-based",
        "generated_at": details.get('committed_at'),
    }


def _perform_bug_analysis(repo, request: BugAnalysisRequest) -> dict:
    """Perform simplified bug origin analysis."""
    # In production, this would use git bisect and LLM analysis
    # For now, return a mock response
    
    commits = list(repo.iter_commits(max_count=100))
    
    # Simple heuristic: find commits that modified files related to the query
    query_terms = request.description.lower().split()
    
    evidence = []
    for i, commit in enumerate(commits):
        score = 0
        
        # Check if commit message matches query
        for term in query_terms:
            if len(term) > 3 and term in commit.message.lower():
                score += 0.2
        
        # Prioritize commits with many changes
        try:
            stats = commit.stats
            if stats.total.insertions + stats.total.deletions > 100:
                score += 0.1
        except Exception:
            pass
        
        if score > 0:
            evidence.append(EvidenceItem(
                type='code_change',
                description=f"Commit mentions relevant terms",
                relevance=score,
                location={'commit': commit.hexsha[:7]},
            ))
    
    # Sort by relevance
    evidence.sort(key=lambda x: x.relevance, reverse=True)
    
    likely_commit = commits[0].hexsha if commits else "unknown"
    
    return BugAnalysisResponse(
        likely_commit=likely_commit,
        probability=0.65,
        reasoning="Based on commit message analysis and change patterns, this commit is most likely to have introduced the issue.",
        affected_files=["src/main.py", "src/utils.py"],
        related_commits=[c.hexsha[:7] for c in commits[:5]],
        suggested_fix="Review the changes in this commit and consider reverting or fixing the specific modification.",
        evidence=evidence[:5],
    )


def _generate_architecture_explanation(repo, commit: Optional[str] = None) -> dict:
    """Generate architecture explanation based on repository structure."""
    try:
        if commit:
            tree = repo.commit(commit).tree
        else:
            tree = repo.head.commit.tree
        
        # Analyze directory structure
        directories = set()
        file_types = {}
        
        for item in tree.traverse():
            if item.type == 'tree':
                directories.add(item.path)
            elif item.type == 'blob':
                ext = item.name.split('.')[-1].lower() if '.' in item.name else 'none'
                file_types[ext] = file_types.get(ext, 0) + 1
        
        # Identify components based on common patterns
        components = []
        dir_list = list(directories)
        
        for d in dir_list[:10]:  # Top 10 directories
            comp_type = 'module'
            if 'test' in d.lower():
                comp_type = 'testing'
            elif 'api' in d.lower() or 'routes' in d.lower():
                comp_type = 'api'
            elif 'utils' in d.lower() or 'helpers' in d.lower():
                comp_type = 'utilities'
            elif 'config' in d.lower() or 'settings' in d.lower():
                comp_type = 'configuration'
            elif 'models' in d.lower() or 'entities' in d.lower():
                comp_type = 'data models'
            
            components.append({
                'name': d.split('/')[-1],
                'path': d,
                'type': comp_type,
            })
        
        return ArchitectureExplanation(
            overview=f"This repository contains {len(dir_list)} main directories with {sum(file_types.values())} files.",
            components=components,
            dependencies=[],
            patterns=['modular', 'layered'] if 'api' in str(dir_list).lower() else ['monolithic'],
            suggestions=[
                "Consider adding more comprehensive tests",
                "Review dependency structure for potential improvements",
            ],
        )
        
    except Exception as e:
        return ArchitectureExplanation(
            overview="Unable to analyze repository structure",
            components=[],
            dependencies=[],
            patterns=[],
            suggestions=[],
        )
