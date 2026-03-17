"""Token influence calculation using Delta H metric."""

from typing import List, Dict, Any, Tuple, Optional

import numpy as np

from app.models.wrapper import LLMModelWrapper
from app.analyzer.hooks import ActivationHookManager
from app.analyzer.entropy import calculate_normalized_activation_entropy
from app.core.logging import logger


class TokenInfluenceAnalyzer:
    """Calculates per-token influence on each layer using entropy difference."""

    def __init__(self, model_name: str):
        self.llm_wrapper = LLMModelWrapper(model_name)
        if not self.llm_wrapper.is_local:
            raise ValueError(
                "TokenInfluenceAnalyzer requires a local LLM for activation access."
            )
        self.hook_manager = ActivationHookManager(self.llm_wrapper.model)
        self.tokenizer = self.llm_wrapper.tokenizer
        self.device = self.llm_wrapper.device

    async def _get_layer_entropies(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict[int, np.ndarray]:
        """Get entropy values for each layer given a prompt."""
        import torch

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)

        activations, _ = await self.hook_manager.run_and_collect(
            inputs.input_ids, inputs.attention_mask
        )

        layer_entropies: Dict[int, np.ndarray] = {}
        for layer_idx, activation_tensor in activations.items():
            act_np = activation_tensor.numpy()
            token_entropies = calculate_normalized_activation_entropy(act_np)
            layer_entropies[layer_idx] = token_entropies.squeeze(0)

        return layer_entropies

    async def analyze(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
        """
        Analyze token influence across layers.
        Returns:
            Tuple of (token_influence_scores, tokens, layer_names)
        """
        original_tokens = self.tokenizer.tokenize(prompt)

        # Get base entropies
        base_entropies = await self._get_layer_entropies(prompt, system_prompt)

        token_influence_scores: List[Dict[str, Any]] = []
        layer_names = [f"Layer {i}" for i in sorted(base_entropies.keys())]

        # Calculate Delta H for each token
        for i, token_to_remove in enumerate(original_tokens):
            modified_tokens = original_tokens[:i] + original_tokens[i + 1:]
            modified_prompt = self.tokenizer.convert_tokens_to_string(modified_tokens)

            modified_entropies = await self._get_layer_entropies(
                modified_prompt, system_prompt
            )

            influence_per_layer: Dict[str, float] = {}
            for layer_idx in sorted(base_entropies.keys()):
                base_h = float(np.mean(base_entropies[layer_idx]))
                modified_h = float(
                    np.mean(modified_entropies.get(layer_idx, np.array(0.0)))
                )
                delta_h = base_h - modified_h
                influence_per_layer[f"Layer {layer_idx}"] = delta_h

            token_influence_scores.append(
                {"token": token_to_remove, "influence_by_layer": influence_per_layer}
            )

        return token_influence_scores, original_tokens, layer_names
