"""Heuristic-based detection for structural anomalies."""

from typing import Dict, List, Any, Optional


class HeuristicAnalyzer:
    """Detects prompt injection via heuristic analysis of prompt structure."""

    def __init__(self) -> None:
        self.suspicious_verbs: List[str] = [
            "reveal", "extract", "dump", "bypass", "disregard",
            "override", "leak", "exfiltrate", "hack", "jailbreak",
        ]
        self.role_switching_phrases: List[str] = [
            "you are now", "act as a", "assume the role of",
            "pretend to be", "from now on you are",
        ]

    async def scan(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Analyze prompt using heuristic rules."""
        score = 0.0
        detected_heuristics: List[str] = []
        lower_prompt = prompt.lower()

        # Heuristic 1: Instruction Conflict Detection
        if "ignore" in lower_prompt and "instruction" in lower_prompt:
            score += 0.3
            detected_heuristics.append("instruction_conflict")

        # Heuristic 2: Role Switching Detection
        if any(phrase in lower_prompt for phrase in self.role_switching_phrases):
            score += 0.25
            detected_heuristics.append("role_switching")

        # Heuristic 3: Suspicious Verbs
        if any(verb in lower_prompt for verb in self.suspicious_verbs):
            score += 0.2
            detected_heuristics.append("suspicious_verb")

        # Heuristic 4: Length Anomaly
        if len(prompt) > 500:
            score += 0.1
            detected_heuristics.append("length_anomaly")

        # Heuristic 5: Context-aware analysis
        if (
            system_prompt
            and ("ignore" in lower_prompt or "override" in lower_prompt)
            and system_prompt.lower() in lower_prompt
        ):
            score += 0.35
            detected_heuristics.append("system_prompt_override_attempt")

        # Heuristic 6: Encoding/obfuscation detection
        if any(c in prompt for c in ["\u200b", "\u200c", "\u200d", "\ufeff"]):
            score += 0.3
            detected_heuristics.append("unicode_obfuscation")

        # Heuristic 7: Excessive special characters
        special_count = sum(1 for c in prompt if not c.isalnum() and not c.isspace())
        if len(prompt) > 0 and special_count / len(prompt) > 0.3:
            score += 0.15
            detected_heuristics.append("excessive_special_chars")

        return {"score": min(score, 1.0), "detected_heuristics": detected_heuristics}
