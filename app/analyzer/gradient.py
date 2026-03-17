"""Gradient-based analysis for token sensitivity."""

from typing import List, Any

from app.core.logging import logger


class GradientAnalyzer:
    """Calculates gradients of model output with respect to input tokens."""

    def __init__(self, model: Any, tokenizer: Any):
        self.model = model
        self.tokenizer = tokenizer
        self.device = next(model.parameters()).device

    def calculate_token_gradients(self, prompt: str, target_class: int = 1) -> List[float]:
        """
        Calculate gradient magnitudes for each input token.
        Args:
            prompt: The input prompt string.
            target_class: Index of the target class or token.
        Returns:
            List of gradient magnitudes per token.
        """
        import torch

        self.model.zero_grad()

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        input_ids = inputs.input_ids

        if hasattr(self.model, "get_input_embeddings"):
            embeddings = self.model.get_input_embeddings()(input_ids)
        else:
            raise NotImplementedError(
                "Model does not have an accessible input embedding layer."
            )

        embeddings = embeddings.detach().requires_grad_(True)

        outputs = self.model(
            inputs_embeds=embeddings, attention_mask=inputs.attention_mask
        )
        logits = outputs.logits

        if logits.dim() == 3:
            target_logit = logits[0, -1, target_class]
        elif logits.dim() == 2:
            target_logit = logits[0, target_class]
        else:
            raise ValueError("Unexpected logits dimension.")

        target_logit.backward()

        if embeddings.grad is not None:
            token_gradients = embeddings.grad.sum(dim=-1).squeeze().abs().tolist()
            if isinstance(token_gradients, float):
                token_gradients = [token_gradients]
            return token_gradients
        else:
            logger.warning("No gradients computed for embeddings.")
            return [0.0] * input_ids.shape[1]
