"""Heatmap generation and data preparation for frontend visualization."""

from typing import List, Dict, Any

import numpy as np


def generate_heatmap_data(
    token_influence_scores: List[Dict[str, Any]],
    tokens: List[str],
    layers: List[str],
) -> List[List[float]]:
    """
    Convert token influence scores into a 2D matrix for heatmap visualization.
    Args:
        token_influence_scores: List of dicts with 'token' and 'influence_by_layer'.
        tokens: Ordered list of tokens (X-axis labels).
        layers: Ordered list of layer names (Y-axis labels).
    Returns:
        2D list (matrix) where rows=layers, columns=tokens.
    """
    num_layers = len(layers)
    num_tokens = len(tokens)
    heatmap_matrix = np.zeros((num_layers, num_tokens))

    layer_to_idx = {layer_name: i for i, layer_name in enumerate(layers)}
    token_to_idx = {token_name: i for i, token_name in enumerate(tokens)}

    for token_score_entry in token_influence_scores:
        token_name = token_score_entry["token"]
        if token_name in token_to_idx:
            col_idx = token_to_idx[token_name]
            for layer_name, influence_value in token_score_entry[
                "influence_by_layer"
            ].items():
                if layer_name in layer_to_idx:
                    row_idx = layer_to_idx[layer_name]
                    heatmap_matrix[row_idx, col_idx] = influence_value

    return heatmap_matrix.tolist()


def generate_mock_heatmap_data(
    tokens: List[str], num_layers: int = 6
) -> tuple[List[List[float]], List[str]]:
    """
    Generate mock heatmap data for demonstration purposes.
    Returns:
        Tuple of (heatmap_matrix, layer_names)
    """
    layers = [f"Layer {i}" for i in range(num_layers)]
    rng = np.random.default_rng(42)
    heatmap_matrix = rng.standard_normal((num_layers, len(tokens)))

    # Make some tokens more influential
    for i, token in enumerate(tokens):
        lower = token.lower().strip()
        if lower in ["ignore", "bypass", "override", "reveal", "hack", "extract"]:
            heatmap_matrix[:, i] *= 3.0

    return heatmap_matrix.tolist(), layers
