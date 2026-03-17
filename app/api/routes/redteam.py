"""Red Team endpoint - /api/v1/redteam."""

from fastapi import APIRouter, HTTPException, status

from app.api.schemas import RedTeamConfig, RedTeamResult
from app.redteam.search import RedTeamGeneticAlgorithm
from app.storage.postgres_db import store_redteam_result
from app.core.logging import logger

router = APIRouter()


@router.post("/redteam", response_model=RedTeamResult)
async def run_red_team_campaign(config: RedTeamConfig) -> RedTeamResult:
    """Run an automated red team campaign using genetic algorithms."""
    try:
        red_team_engine = RedTeamGeneticAlgorithm(config)
        best_prompt, success_rate, generations, details = await red_team_engine.run()

        # Store result
        await store_redteam_result(
            config=config.model_dump(),
            best_prompt=best_prompt,
            best_fitness=success_rate,
            generations=generations,
            evaluation_details=details,
        )

        return RedTeamResult(
            best_attack_prompt=best_prompt,
            attack_success_rate=success_rate,
            generations_run=generations,
            attack_details=details,
        )
    except Exception as e:
        logger.error(f"Red Team campaign failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
