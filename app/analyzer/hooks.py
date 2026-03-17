"""PyTorch model hooking utilities for extracting intermediate activations."""

from typing import Dict, List, Tuple, Any, Callable

from app.core.logging import logger


class ActivationHookManager:
    """Manages PyTorch forward hooks for extracting layer activations and attention maps."""

    def __init__(self, model: Any):
        self.model = model
        self.activations: Dict[int, Any] = {}
        self.attention_maps: Dict[int, Any] = {}
        self.hooks: List[Any] = []

    def _register_forward_hook(self, layer_idx: int) -> Callable:
        def hook_fn(module: Any, input: Any, output: Any) -> None:
            if isinstance(output, tuple):
                hidden_state = output[0]
                if len(output) > 1 and isinstance(output[1], tuple):
                    self.attention_maps[layer_idx] = output[1][0].detach().cpu()
                self.activations[layer_idx] = hidden_state.detach().cpu()
            else:
                self.activations[layer_idx] = output.detach().cpu()

        return hook_fn

    def register_hooks(self) -> None:
        """Register forward hooks on all transformer layers."""
        self.remove_hooks()
        self.activations.clear()
        self.attention_maps.clear()

        layers = self._get_layers()
        for i, layer in enumerate(layers):
            hook = layer.register_forward_hook(self._register_forward_hook(i))
            self.hooks.append(hook)

        logger.info(f"Registered hooks for {len(self.hooks)} layers.")

    def _get_layers(self) -> list:
        """Get transformer layers from various model architectures."""
        if hasattr(self.model, "model") and hasattr(self.model.model, "layers"):
            return list(self.model.model.layers)
        elif hasattr(self.model, "transformer") and hasattr(self.model.transformer, "h"):
            return list(self.model.transformer.h)
        elif hasattr(self.model, "gpt_neox") and hasattr(self.model.gpt_neox, "layers"):
            return list(self.model.gpt_neox.layers)
        else:
            raise ValueError("Unsupported model architecture for hook registration.")

    def remove_hooks(self) -> None:
        """Remove all registered hooks."""
        for hook in self.hooks:
            hook.remove()
        self.hooks.clear()

    def get_activations(self) -> Dict[int, Any]:
        return self.activations

    def get_attention_maps(self) -> Dict[int, Any]:
        return self.attention_maps

    async def run_and_collect(
        self, input_ids: Any, attention_mask: Any
    ) -> Tuple[Dict[int, Any], Dict[int, Any]]:
        """Run a forward pass and collect activations and attention maps."""
        import torch

        self.register_hooks()
        with torch.no_grad():
            self.model.eval()
            self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_attentions=True,
                output_hidden_states=True,
            )
        self.remove_hooks()
        return self.get_activations(), self.get_attention_maps()
