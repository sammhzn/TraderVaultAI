from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from app.ai.experiment_runner import (
    Experiment,
    ExperimentResult,
    ExperimentRunner,
)
from app.ai.parameter_search import ParameterSearch


@dataclass
class ResearchRun:
    """
    Stores the complete result of a research session.
    """

    experiments: List[Experiment]
    results: List[ExperimentResult]
    best_result: Optional[ExperimentResult]

    @property
    def profitable_results(
        self,
    ) -> List[ExperimentResult]:
        """
        Return all experiments that produced
        positive net profit.
        """

        return [
            result
            for result in self.results
            if result.net_profit > 0
        ]

class ResearchEngine:
    """
    Coordinates parameter search and experiment execution.

    Flow:

        Parameter space
              ↓
        ParameterSearch
              ↓
        Experiments
              ↓
        ExperimentRunner
              ↓
        Backtest results
              ↓
        Best result
    """

    def __init__(
        self,
        backtest_function: Optional[
            Callable[[Dict[str, Any]], Any]
        ] = None,
    ):
        self.backtest_function = backtest_function

        self.parameter_search = ParameterSearch()

        self.experiment_runner = ExperimentRunner(
            backtest_function=backtest_function
        )

    def create_experiments(
        self,
        parameters: Dict[str, List[Any]],
    ) -> List[Experiment]:
        """
        Convert parameter search combinations into
        Experiment objects.

        The Experiment config is always a normal
        dictionary so the backtest function can use:

            config["rr"]

        instead of receiving a ParameterCombination object.
        """

        self.parameter_search.set_parameters(
            parameters
        )

        combinations = (
            self.parameter_search.generate()
        )

        experiments = []

        for index, combination in enumerate(
            combinations,
            start=1,
        ):

            experiments.append(
                Experiment(
                    name=f"Experiment-{index}",
                    config=dict(
                        combination.parameters
                    ),
                )
            )

        return experiments

    def run(
        self,
        parameters: Dict[str, List[Any]],
    ) -> ResearchRun:
        """
        Run every parameter combination.
        """

        experiments = self.create_experiments(
            parameters
        )

        # Clear previous results so separate research
        # runs do not contaminate each other.
        self.experiment_runner.results.clear()

        results = self.experiment_runner.run(
            experiments
        )

        best_result = (
            self.experiment_runner.best_by_profit()
        )

        return ResearchRun(
            experiments=experiments,
            results=results,
            best_result=best_result,
        )