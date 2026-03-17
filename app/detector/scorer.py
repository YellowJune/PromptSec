"""Aggregates scores from all detector layers for final risk assessment."""

from typing import Tuple, Dict, Any, Optional

from app.detector.rule_engine import RuleEngine
from app.detector.heuristic import HeuristicAnalyzer
from app.detector.llm_classifier import LLMClassifier
from app.core.config import settings
from app.core.logging import logger


class PromptScorer:
    """Combines rule-based, heuristic, and LLM-based detection scores."""

    def __init__(self, model_name: str):
        self.rule_engine = RuleEngine()
        self.heuristic_analyzer = HeuristicAnalyzer()
        self.llm_classifier = LLMClassifier(model_name)
        self._use_llm = True

    async def scan(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Tuple[float, str, Dict[str, Any]]:
        """Run all detection layers and return aggregated result."""
        rule_result = await self.rule_engine.scan(prompt)
        heuristic_result = await self.heuristic_analyzer.scan(prompt, system_prompt)

        # Try LLM classification, fall back gracefully
        llm_classification_result: Dict[str, Any] = {
            "is_attack": False,
            "confidence": 0.0,
            "attack_types": [],
        }
        if self._use_llm:
            try:
                llm_classification_result = await self.llm_classifier.classify(
                    prompt, system_prompt
                )
            except Exception as e:
                logger.warning(f"LLM classifier unavailable, using rule+heuristic only: {e}")
                self._use_llm = False

        # Aggregate scores with predefined weights
        if self._use_llm:
            risk_score = (
                settings.DETECTOR_RULE_WEIGHT * rule_result["score"]
                + settings.DETECTOR_HEURISTIC_WEIGHT * heuristic_result["score"]
                + settings.DETECTOR_LLM_WEIGHT * llm_classification_result["confidence"]
            )
        else:
            # Redistribute weights when LLM is unavailable
            total_weight = settings.DETECTOR_RULE_WEIGHT + settings.DETECTOR_HEURISTIC_WEIGHT
            risk_score = (
                (settings.DETECTOR_RULE_WEIGHT / total_weight) * rule_result["score"]
                + (settings.DETECTOR_HEURISTIC_WEIGHT / total_weight) * heuristic_result["score"]
            )

        risk_score = min(risk_score, 1.0)

        # Determine final label
        label = "safe"
        if risk_score >= settings.DETECTOR_RISK_THRESHOLD:
            label = "attack"
        elif risk_score > 0.1:
            label = "suspicious"

        details = {
            "rule_engine": rule_result,
            "heuristic_analyzer": heuristic_result,
            "llm_classifier": llm_classification_result,
        }

        return risk_score, label, details
