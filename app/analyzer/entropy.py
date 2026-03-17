"""Entropy calculation functions for activations and attention weights."""

from typing import Dict, Callable

import numpy as np


def calculate_attention_entropy(attention_weights: np.ndarray) -> np.ndarray:
    """
    Calculate Shannon entropy for attention weights.
    Args:
        attention_weights: Array of shape (batch_size, num_heads, seq_len, seq_len)
    Returns:
        Array of shape (batch_size, num_heads, seq_len) - entropy per token per head.
    """
    epsilon = 1e-9
    normalized_weights = attention_weights + epsilon
    normalized_weights = normalized_weights / normalized_weights.sum(axis=-1, keepdims=True)
    entropy = -np.sum(normalized_weights * np.log(normalized_weights), axis=-1)
    return entropy


def calculate_activation_variance_entropy(activations: np.ndarray) -> np.ndarray:
    """
    Calculate variance of activations as a proxy for entropy.
    Args:
        activations: Array of shape (batch_size, seq_len, hidden_dim)
    Returns:
        Array of shape (batch_size, seq_len) - variance per token.
    """
    variance = np.var(activations, axis=-1)
    return np.log(variance + 1e-9)


def calculate_normalized_activation_entropy(activations: np.ndarray) -> np.ndarray:
    """
    Calculate entropy from normalized activations.
    Args:
        activations: Array of shape (batch_size, seq_len, hidden_dim)
    Returns:
        Array of shape (batch_size, seq_len) - entropy per token.
    """
    min_val = activations.min(axis=-1, keepdims=True)
    max_val = activations.max(axis=-1, keepdims=True)
    scaled = (activations - min_val) / (max_val - min_val + 1e-9)

    sum_scaled = scaled.sum(axis=-1, keepdims=True)
    prob_like = scaled / (sum_scaled + 1e-9)

    epsilon = 1e-9
    entropy = -np.sum(prob_like * np.log(prob_like + epsilon), axis=-1)
    return entropy


def get_average_layer_entropy(
    layer_activations: Dict[int, np.ndarray],
    entropy_fn: Callable[[np.ndarray], np.ndarray],
) -> Dict[int, float]:
    """Compute average entropy per layer."""
    avg_entropies: Dict[int, float] = {}
    for layer_idx, activations in layer_activations.items():
        token_entropies = entropy_fn(activations)
        avg_entropies[layer_idx] = float(np.mean(token_entropies))
    return avg_entropies
