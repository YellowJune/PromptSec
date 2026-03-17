"""SQLite/PostgreSQL database interaction layer using SQLAlchemy."""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.logging import logger

# In-memory storage for now (can be replaced with SQLAlchemy + PostgreSQL)
_prompt_store: Dict[str, Dict[str, Any]] = {}
_analysis_store: Dict[str, Dict[str, Any]] = {}
_redteam_store: Dict[str, Dict[str, Any]] = {}


async def init_db() -> None:
    """Initialize database connection."""
    logger.info("Database initialized (in-memory store).")


async def store_prompt_result(
    prompt_text: str,
    system_prompt_text: Optional[str],
    model_name: str,
    risk_score: float,
    detection_label: str,
    detection_details: Dict[str, Any],
) -> str:
    """Store a prompt detection result."""
    record_id = str(uuid.uuid4())
    _prompt_store[record_id] = {
        "id": record_id,
        "prompt_text": prompt_text,
        "system_prompt_text": system_prompt_text,
        "model_name": model_name,
        "risk_score": risk_score,
        "detection_label": detection_label,
        "detection_details": detection_details,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return record_id


async def store_analysis_result(
    prompt_id: str, analysis_data: Dict[str, Any]
) -> str:
    """Store a flow analysis result."""
    record_id = str(uuid.uuid4())
    _analysis_store[record_id] = {
        "id": record_id,
        "prompt_id": prompt_id,
        "analysis_data": analysis_data,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return record_id


async def store_redteam_result(
    config: Dict[str, Any],
    best_prompt: str,
    best_fitness: float,
    generations: int,
    evaluation_details: Dict[str, Any],
) -> str:
    """Store a red team campaign result."""
    record_id = str(uuid.uuid4())
    _redteam_store[record_id] = {
        "id": record_id,
        "config": config,
        "best_prompt_found": best_prompt,
        "best_fitness_score": best_fitness,
        "generations_run": generations,
        "final_evaluation_details": evaluation_details,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return record_id


async def get_recent_prompts(limit: int = 50) -> list:
    """Get recent prompt results."""
    results = sorted(
        _prompt_store.values(), key=lambda x: x["created_at"], reverse=True
    )
    return results[:limit]


async def get_recent_analyses(limit: int = 50) -> list:
    """Get recent analysis results."""
    results = sorted(
        _analysis_store.values(), key=lambda x: x["created_at"], reverse=True
    )
    return results[:limit]
