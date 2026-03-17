"""Unified interface for interacting with different LLMs."""

import json
from typing import Union, Dict, Any, List, Tuple, Optional

from app.models.loader import get_llm_model
from app.core.logging import logger


class LLMModelWrapper:
    """Provides a unified interface for LLM inference and hook registration."""

    def __init__(self, model_identifier: str):
        self.model_identifier = model_identifier
        self.model_info = get_llm_model(model_identifier)

        if isinstance(self.model_info, dict) and "model" in self.model_info:
            self.model = self.model_info["model"]
            self.tokenizer = self.model_info["tokenizer"]
            self.is_local = True

            import torch
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            self.model.eval()
        else:
            # Assume it's an OpenAI client or similar API client
            self.client = self.model_info
            self.is_local = False

    async def generate_text(
        self,
        prompt: str,
        max_new_tokens: int = 50,
        temperature: float = 0.7,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        """Generate text from prompt using the loaded model."""
        if self.is_local:
            import torch

            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=temperature > 0,
                )
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        else:
            # OpenAI API call
            messages = [{"role": "user", "content": prompt}]
            kwargs: Dict[str, Any] = {
                "model": self.model_identifier,
                "messages": messages,
                "max_tokens": max_new_tokens,
                "temperature": temperature,
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""

    def get_llm_output_with_activations(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Tuple["torch.Tensor", Dict[int, "torch.Tensor"], Dict[int, "torch.Tensor"]]:
        """Extract activations and attention maps via forward hooks."""
        import torch

        if not self.is_local:
            raise NotImplementedError(
                "Activation extraction is only supported for local HuggingFace models."
            )

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)

        activations: Dict[int, torch.Tensor] = {}
        attention_maps: Dict[int, torch.Tensor] = {}
        hooks = []

        # Get the transformer layers
        layers = self._get_model_layers()

        for i, layer in enumerate(layers):
            def save_activation_hook(module: Any, input: Any, output: Any, layer_idx: int = i) -> None:
                if isinstance(output, tuple):
                    activations[layer_idx] = output[0].detach().cpu()
                else:
                    activations[layer_idx] = output.detach().cpu()

            hooks.append(layer.register_forward_hook(save_activation_hook))

        with torch.no_grad():
            output = self.model(
                **inputs, output_attentions=True, output_hidden_states=True
            )

        for hook in hooks:
            hook.remove()

        final_output = (
            output.logits if hasattr(output, "logits") else output.last_hidden_state
        )

        # Extract attention from model output
        if hasattr(output, "attentions") and output.attentions is not None:
            for i, attn in enumerate(output.attentions):
                attention_maps[i] = attn.detach().cpu()

        return final_output.cpu(), activations, attention_maps

    def _get_model_layers(self) -> list:
        """Get transformer layers from various model architectures."""
        if hasattr(self.model, "model") and hasattr(self.model.model, "layers"):
            return list(self.model.model.layers)
        elif hasattr(self.model, "transformer") and hasattr(
            self.model.transformer, "h"
        ):
            return list(self.model.transformer.h)
        elif hasattr(self.model, "gpt_neox") and hasattr(
            self.model.gpt_neox, "layers"
        ):
            return list(self.model.gpt_neox.layers)
        else:
            raise ValueError("Unsupported model architecture for hook registration.")

    def tokenize_prompt(self, prompt: str) -> List[str]:
        if not self.is_local:
            raise NotImplementedError(
                "Tokenization is only supported for local HuggingFace models."
            )
        return self.tokenizer.tokenize(prompt)

    def get_token_ids(self, prompt: str) -> "torch.Tensor":
        import torch

        if not self.is_local:
            raise NotImplementedError(
                "Token ID retrieval is only supported for local HuggingFace models."
            )
        return self.tokenizer(prompt, return_tensors="pt").input_ids.squeeze().to(
            self.device
        )

    def decode_token_ids(self, token_ids: "torch.Tensor") -> str:
        if not self.is_local:
            raise NotImplementedError(
                "Token decoding is only supported for local HuggingFace models."
            )
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)
