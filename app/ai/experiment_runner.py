from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Experiment:
    """
    Defines one strategy experiment.

    Each experiment has a name and a configuration.
    """

    name: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentResult:
    """
    Stores the result of one completed experiment.
    """

    experiment: Experiment
    total_trades: int
    wins: int
    losses: int
    net_profit: float
    profit_factor: float


class ExperimentRunner:
    """
    Runs multiple strategy experiments and collects results.

    The backtest function receives the experiment configuration
    as a normal dictionary.
    """

    def __init__(
        self,
        backtest_function: Optional[
            Callable[[Dict[str, Any]], Any]
        ] = None,
    ):
        self.backtest_function = backtest_function
        self.results: List[ExperimentResult] = []

    def run_experiment(
        self,
        experiment: Experiment,
    ) -> ExperimentResult:
        """
        Run a single experiment.
        """

        if self.backtest_function is None:
            raise RuntimeError(
                "No backtest function has been configured."
            )

        raw_result = self.backtest_function(
            experiment.config
        )

        result = self._build_result(
            experiment,
            raw_result,
        )

        self.results.append(result)

        return result

    def run(
        self,
        experiments: List[Experiment],
    ) -> List[ExperimentResult]:
        """
        Run all supplied experiments.

        Main interface used by ResearchEngine.
        """

        return self.run_all(experiments)

    def run_all(
        self,
        experiments: List[Experiment],
    ) -> List[ExperimentResult]:
        """
        Run every experiment in the supplied list.
        """

        results = []

        for experiment in experiments:
            result = self.run_experiment(
                experiment
            )

            results.append(result)

        return results

    def _build_result(
        self,
        experiment: Experiment,
        raw_result: Any,
    ) -> ExperimentResult:
        """
        Convert backtest output into ExperimentResult.
        """

        if isinstance(raw_result, dict):

            total_trades = int(
                raw_result.get(
                    "total_trades",
                    0,
                )
            )

            wins = int(
                raw_result.get(
                    "wins",
                    0,
                )
            )

            losses = int(
                raw_result.get(
                    "losses",
                    0,
                )
            )

            net_profit = float(
                raw_result.get(
                    "net_profit",
                    0.0,
                )
            )

            profit_factor = float(
                raw_result.get(
                    "profit_factor",
                    0.0,
                )
            )

        else:

            total_trades = int(
                getattr(
                    raw_result,
                    "total_trades",
                    0,
                )
            )

            wins = int(
                getattr(
                    raw_result,
                    "wins",
                    0,
                )
            )

            losses = int(
                getattr(
                    raw_result,
                    "losses",
                    0,
                )
            )

            net_profit = float(
                getattr(
                    raw_result,
                    "net_profit",
                    0.0,
                )
            )

            profit_factor = float(
                getattr(
                    raw_result,
                    "profit_factor",
                    0.0,
                )
            )

        return ExperimentResult(
            experiment=experiment,
            total_trades=total_trades,
            wins=wins,
            losses=losses,
            net_profit=net_profit,
            profit_factor=profit_factor,
        )

    def best_result(
        self,
    ) -> Optional[ExperimentResult]:
        """
        Return the experiment with the highest net profit.
        """

        if not self.results:
            return None

        return max(
            self.results,
            key=lambda result: result.net_profit,
        )

    def best_by_profit(
        self,
    ) -> Optional[ExperimentResult]:
        """
        Alias used by ResearchEngine.

        Returns the experiment with the highest
        net profit.
        """

        return self.best_result()

    def profitable_results(
        self,
    ) -> List[ExperimentResult]:
        """
        Return experiments that produced positive
        net profit.
        """

        return [
            result
            for result in self.results
            if result.net_profit > 0
        ]