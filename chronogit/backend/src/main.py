"""
ChronoGit Backend Entry Point
"""

import uvicorn
from .api.app import app


def main():
    """Run the ChronoGit API server."""
    uvicorn.run(
        "backend.src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
