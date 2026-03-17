"""Analysis endpoint - /api/v1/analyze."""

from fastapi import APIRouter, HTTPException, status

from app.api.schemas import PromptInput, AnalysisResult
from app.analyzer.visualizer import generate_heatmap_data, generate_mock_heatmap_data
from app.core.logging import logger
from app.models.loader import is_model_loaded

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_prompt_flow(input_data: PromptInput) -> AnalysisResult:
    """Analyze prompt information flow through LLM layers."""
    try:
        # Check if a local model is available for deep analysis
        if is_model_loaded(input_data.model_name):
            from app.analyzer.influence import TokenInfluenceAnalyzer

            analyzer = TokenInfluenceAnalyzer(input_data.model_name)
            token_influence_scores, tokens, layers = await analyzer.analyze(
                input_data.prompt, input_data.system_prompt
            )
            heatmap_matrix = generate_heatmap_data(
                token_influence_scores, tokens, layers
            )
        else:
            # Use mock/simulated analysis when no local model available
            logger.info(
                f"Model '{input_data.model_name}' not loaded locally. "
                "Using simulated analysis."
            )
            tokens = input_data.prompt.split()
            heatmap_matrix, layers = generate_mock_heatmap_data(tokens, num_layers=6)
            token_influence_scores = []
            for i, token in enumerate(tokens):
                influence_by_layer = {}
                for j, layer in enumerate(layers):
                    influence_by_layer[layer] = heatmap_matrix[j][i]
                token_influence_scores.append(
                    {"token": token, "influence_by_layer": influence_by_layer}
                )

        return AnalysisResult(
            prompt=input_data.prompt,
            model_name=input_data.model_name,
            token_influence_scores=token_influence_scores,
            heatmap_data=heatmap_matrix,
            tokens=tokens,
            layers=layers,
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
