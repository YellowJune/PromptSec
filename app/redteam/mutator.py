"""Prompt transformation/mutation functions for genetic algorithm."""

import random
from typing import List, Tuple


class PromptMutator:
    """Applies mutations and crossover operations to prompts."""

    def __init__(self) -> None:
        self.synonyms = {
            "ignore": ["disregard", "override", "neglect", "skip", "forget"],
            "reveal": ["disclose", "uncover", "show", "leak", "expose"],
            "system": ["core", "internal", "base", "root", "main"],
            "instructions": ["directives", "commands", "guidelines", "rules", "prompts"],
            "bypass": ["circumvent", "avoid", "evade", "sidestep", "skip"],
        }
        self.obfuscation_techniques = [
            lambda s: " ".join(s),
            lambda s: s.replace("i", "1").replace("o", "0"),
            lambda s: s.upper(),
            lambda s: s.lower(),
            lambda s: s + random.choice([".", "!", "?"]),
            lambda s: s[::-1],
        ]

    def mutate_prompt(self, prompt: str, mutation_rate: float = 0.1) -> str:
        """Apply random mutations to a prompt."""
        tokens = prompt.split()
        mutated_tokens: List[str] = []
        for token in tokens:
            if random.random() < mutation_rate:
                if token.lower() in self.synonyms and random.random() < 0.5:
                    mutated_tokens.append(random.choice(self.synonyms[token.lower()]))
                elif random.random() < 0.3:
                    mutated_tokens.append(
                        random.choice(self.obfuscation_techniques)(token)
                    )
                else:
                    mutated_tokens.append(token)
            else:
                mutated_tokens.append(token)
        return " ".join(mutated_tokens)

    def crossover_prompts(self, prompt1: str, prompt2: str) -> Tuple[str, str]:
        """Perform single-point crossover between two prompts."""
        tokens1 = prompt1.split()
        tokens2 = prompt2.split()

        min_len = min(len(tokens1), len(tokens2))
        if min_len < 2:
            return prompt1, prompt2

        crossover_point = random.randint(1, min_len - 1)

        new_prompt1 = " ".join(tokens1[:crossover_point] + tokens2[crossover_point:])
        new_prompt2 = " ".join(tokens2[:crossover_point] + tokens1[crossover_point:])

        return new_prompt1, new_prompt2
