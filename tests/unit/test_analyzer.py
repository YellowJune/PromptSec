"""Unit tests for the Analyzer module."""

import numpy as np
import pytest

from app.analyzer.entropy import (
    calculate_attention_entropy,
    calculate_activation_variance_entropy,
    calculate_normalized_activation_entropy,
)
from app.analyzer.visualizer import generate_heatmap_data, generate_mock_heatmap_data


class TestEntropy:
    def test_attention_entropy(self):
        # Uniform attention -> max entropy
        weights = np.ones((1, 2, 4, 4)) / 4.0
        entropy = calculate_attention_entropy(weights)
        assert entropy.shape == (1, 2, 4)
        # Entropy of uniform dist over 4 items ≈ ln(4) ≈ 1.386
        assert np.allclose(entropy, np.log(4), atol=0.1)

    def test_attention_entropy_focused(self):
        # Focused attention -> low entropy
        weights = np.zeros((1, 1, 3, 3))
        weights[0, 0, :, 0] = 1.0  # All attention on first token
        entropy = calculate_attention_entropy(weights)
        assert entropy.shape == (1, 1, 3)
        # Should be near 0
        assert np.all(entropy < 0.1)

    def test_activation_variance_entropy(self):
        activations = np.random.randn(1, 5, 64)
        entropy = calculate_activation_variance_entropy(activations)
        assert entropy.shape == (1, 5)

    def test_normalized_activation_entropy(self):
        activations = np.random.randn(1, 5, 64)
        entropy = calculate_normalized_activation_entropy(activations)
        assert entropy.shape == (1, 5)
        # Entropy should be positive for random activations
        assert np.all(entropy > 0)


class TestVisualizer:
    def test_generate_heatmap_data(self):
        tokens = ["hello", "world"]
        layers = ["Layer 0", "Layer 1"]
        token_scores = [
            {"token": "hello", "influence_by_layer": {"Layer 0": 0.5, "Layer 1": 0.3}},
            {"token": "world", "influence_by_layer": {"Layer 0": 0.1, "Layer 1": 0.8}},
        ]
        matrix = generate_heatmap_data(token_scores, tokens, layers)
        assert len(matrix) == 2  # 2 layers
        assert len(matrix[0]) == 2  # 2 tokens
        assert matrix[0][0] == 0.5
        assert matrix[1][1] == 0.8

    def test_generate_mock_heatmap_data(self):
        tokens = ["ignore", "all", "instructions"]
        matrix, layers = generate_mock_heatmap_data(tokens, num_layers=4)
        assert len(matrix) == 4
        assert len(matrix[0]) == 3
        assert len(layers) == 4
