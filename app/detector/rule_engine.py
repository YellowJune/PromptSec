"""Rule-based detection using regular expressions."""

import re
from typing import Dict, List, Any


class RuleEngine:
    """Detects prompt injection patterns using regex rules."""

    def __init__(self) -> None:
        self.rules: List[Dict[str, str]] = [
            {"pattern": r"ignore (all )?(previous |prior )?instructions", "label": "instruction_override"},
            {"pattern": r"reveal .* prompt", "label": "data_exfiltration"},
            {"pattern": r"act as .*", "label": "role_switching"},
            {"pattern": r"bypass .* safety", "label": "jailbreak"},
            {"pattern": r"tell me about your system prompt", "label": "data_exfiltration"},
            {"pattern": r"disregard .* (rules|instructions|guidelines)", "label": "instruction_override"},
            {"pattern": r"pretend you (are|have) no (rules|restrictions)", "label": "jailbreak"},
            {"pattern": r"you are now (a |an )?unrestricted", "label": "jailbreak"},
            {"pattern": r"(show|print|output|display) .* (system|initial) (prompt|instructions)", "label": "data_exfiltration"},
            {"pattern": r"override .* (safety|content|output) (filter|policy)", "label": "jailbreak"},
            {"pattern": r"do not follow .* (rules|guidelines|instructions)", "label": "instruction_override"},
            {"pattern": r"forget (all|everything|your) (previous|prior|above)", "label": "instruction_override"},
        ]

    async def scan(self, prompt: str) -> Dict[str, Any]:
        """Scan a prompt against all rules and return score + matched rules."""
        score = 0.0
        matched_rules: List[str] = []
        for rule in self.rules:
            if re.search(rule["pattern"], prompt, re.IGNORECASE):
                score += 0.2
                matched_rules.append(rule["label"])

        return {"score": min(score, 1.0), "matched_rules": matched_rules}
