"""Genetic Algorithm implementation for red team prompt search."""

import random
import asyncio
from typing import List, Tuple, Dict, Any

from app.redteam.generator import PromptGenerator
from app.redteam.mutator import PromptMutator
from app.redteam.evaluator import AttackEvaluator
from app.api.schemas import RedTeamConfig
from app.core.logging import logger


class RedTeamGeneticAlgorithm:
    """Uses evolutionary algorithms to discover effective adversarial prompts."""

    def __init__(self, config: RedTeamConfig):
        self.config = config
        self.prompt_generator = PromptGenerator(
            seed_prompts=[],
            vulnerability_types=[config.target_vulnerability],
        )
        self.prompt_mutator = PromptMutator()
        self.attack_evaluator = AttackEvaluator(
            target_llm_name="default-llm",
            detector_llm_name="default-llm",
        )

    def _create_individual(self) -> Dict[str, Any]:
        """Create an individual (prompt + fitness)."""
        prompt = self.prompt_generator.generate_initial_population(1)[0]
        return {"prompt": prompt, "fitness": 0.0}

    async def _evaluate_individual(self, individual: Dict[str, Any]) -> float:
        """Evaluate fitness of an individual prompt."""
        prompt = individual["prompt"]
        try:
            eval_result = await self.attack_evaluator.evaluate_attack(
                prompt, target_vulnerability=self.config.target_vulnerability
            )

            fitness = 0.0
            if eval_result["attack_success"]:
                fitness += 0.5
            if eval_result["detector_bypassed"]:
                fitness += 0.5

            # Penalize very long prompts
            fitness -= len(prompt) * 0.001
            return fitness
        except Exception as e:
            logger.warning(f"Evaluation failed for prompt: {e}")
            return 0.0

    def _select_tournament(
        self, population: List[Dict[str, Any]], tournament_size: int = 3
    ) -> Dict[str, Any]:
        """Tournament selection."""
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda ind: ind["fitness"])

    async def run(self) -> Tuple[str, float, int, Dict[str, Any]]:
        """Execute the genetic algorithm and return the best adversarial prompt."""
        # Create initial population
        population: List[Dict[str, Any]] = [
            self._create_individual() for _ in range(self.config.population_size)
        ]

        # Evaluate initial population
        for ind in population:
            ind["fitness"] = await self._evaluate_individual(ind)

        for gen in range(self.config.num_generations):
            logger.info(
                f"Red Team Generation {gen + 1}/{self.config.num_generations}"
            )

            # Selection
            offspring: List[Dict[str, Any]] = []
            while len(offspring) < len(population):
                parent1 = self._select_tournament(population)
                parent2 = self._select_tournament(population)

                # Crossover
                if random.random() < self.config.crossover_probability:
                    child1_prompt, child2_prompt = self.prompt_mutator.crossover_prompts(
                        parent1["prompt"], parent2["prompt"]
                    )
                else:
                    child1_prompt = parent1["prompt"]
                    child2_prompt = parent2["prompt"]

                # Mutation
                if random.random() < self.config.mutation_rate:
                    child1_prompt = self.prompt_mutator.mutate_prompt(
                        child1_prompt, self.config.mutation_rate
                    )
                if random.random() < self.config.mutation_rate:
                    child2_prompt = self.prompt_mutator.mutate_prompt(
                        child2_prompt, self.config.mutation_rate
                    )

                offspring.append({"prompt": child1_prompt, "fitness": 0.0})
                offspring.append({"prompt": child2_prompt, "fitness": 0.0})

            offspring = offspring[: len(population)]

            # Evaluate offspring
            for ind in offspring:
                ind["fitness"] = await self._evaluate_individual(ind)

            population = offspring

        # Get best individual
        best_individual = max(population, key=lambda ind: ind["fitness"])
        best_prompt = best_individual["prompt"]
        best_fitness = best_individual["fitness"]

        # Final evaluation
        final_eval = await self.attack_evaluator.evaluate_attack(
            best_prompt, target_vulnerability=self.config.target_vulnerability
        )

        return best_prompt, best_fitness, self.config.num_generations, final_eval
