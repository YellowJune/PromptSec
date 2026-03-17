"""Detection endpoint - /api/v1/detect."""

from fastapi import APIRouter, HTTPException, status

from app.api.schemas import PromptInput, DetectionResult
from app.detector.scorer import PromptScorer
from app.storage.postgres_db import store_prompt_result
from app.core.logging import logger

router = APIRouter()


@router.post("/detect", response_model=DetectionResult)
async def detect_prompt_injection(input_data: PromptInput) -> DetectionResult:
    """Analyze a prompt for potential injection attacks."""
    try:
        scorer = PromptScorer(input_data.model_name)
        risk_score, label, details = await scorer.scan(
            input_data.prompt, input_data.system_prompt
        )

        # Store result
        await store_prompt_result(
            prompt_text=input_data.prompt,
            system_prompt_text=input_data.system_prompt,
            model_name=input_data.model_name,
            risk_score=risk_score,
            detection_label=label,
            detection_details=details,
        )

        return DetectionResult(risk_score=risk_score, label=label, details=details)
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
