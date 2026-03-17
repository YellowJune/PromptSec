"""Handles loading of LLM models and initialization of external API clients."""

from typing import Dict, Any, Optional

from app.core.config import settings
from app.core.logging import logger

# Global storage for loaded models/clients
_llm_models: Dict[str, Any] = {}


async def load_llm_models() -> None:
    """Load HuggingFace local model and/or initialize API clients at startup."""
    logger.info("Loading LLM models...")

    # Load HuggingFace local model
    if settings.HUGGINGFACE_MODEL_PATH:
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(
                settings.HUGGINGFACE_MODEL_PATH,
                token=settings.HUGGINGFACE_TOKEN,
            )
            # Set pad token if not set
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            model = AutoModelForCausalLM.from_pretrained(
                settings.HUGGINGFACE_MODEL_PATH,
                token=settings.HUGGINGFACE_TOKEN,
            )
            _llm_models[settings.HUGGINGFACE_MODEL_PATH] = {
                "tokenizer": tokenizer,
                "model": model,
            }
            logger.info(f"Loaded HuggingFace model: {settings.HUGGINGFACE_MODEL_PATH}")
        except Exception as e:
            logger.warning(f"Failed to load HuggingFace model {settings.HUGGINGFACE_MODEL_PATH}: {e}")

    # Initialize OpenAI client
    if settings.OPENAI_API_KEY:
        try:
            from openai import OpenAI

            _llm_models["openai"] = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("Initialized OpenAI client.")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI client: {e}")

    logger.info(f"LLM model loading complete. Available models: {list(_llm_models.keys())}")


def get_llm_model(model_name: str) -> Any:
    """Retrieve a loaded model/client by name."""
    if model_name not in _llm_models:
        raise ValueError(
            f"Model '{model_name}' not loaded. Available models: {list(_llm_models.keys())}"
        )
    return _llm_models[model_name]


def get_available_models() -> list[str]:
    """Return list of available model names."""
    return list(_llm_models.keys())


def is_model_loaded(model_name: str) -> bool:
    """Check if a model is loaded."""
    return model_name in _llm_models
