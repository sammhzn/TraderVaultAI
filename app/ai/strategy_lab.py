from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StrategyExperiment:
    """
    Describes one strategy experiment.

    An experiment contains a strategy name and a set of parameters
    that can be passed to the backtesting system.
    """

    name: str
    strategy: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class ExperimentResult:
    """
    Stores the measurable result of a strategy experiment.
    """

    experiment: StrategyExperiment

    total_trades: int
    wins: int
    losses: int

    gross_profit: float
    gross_loss: float
    net_profit: float
    profit_factor: float

    win_rate: float = 0.0

    def __post_init__(self):
        if self.total_trades > 0:
            self.win_rate = self.wins / self.total_trades
        else:
            self.win_rate = 0.0


class StrategyLab:
    """
    Registry and comparison layer for strategy experiments.

    This class does not perform trading itself.
    It provides a controlled structure for running and comparing
    different strategy configurations.
    """

    def __init__(self):
        self.experiments: List[StrategyExperiment] = []
        self.results: List[ExperimentResult] = []

    def add_experiment(
        self,
        name: str,
        strategy: str,
        parameters: Optional[Dict[str, Any]] = None,
        description: str = "",
    ) -> StrategyExperiment:

        experiment = StrategyExperiment(
            name=name,
            strategy=strategy,
            parameters=parameters or {},
            description=description,
        )

        self.experiments.append(experiment)

        return experiment

    def add_result(
        self,
        experiment: StrategyExperiment,
        total_trades: int,
        wins: int,
        losses: int,
        gross_profit: float,
        gross_loss: float,
        net_profit: float,
        profit_factor: float,
    ) -> ExperimentResult:

        result = ExperimentResult(
            experiment=experiment,
            total_trades=total_trades,
            wins=wins,
            losses=losses,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            net_profit=net_profit,
            profit_factor=profit_factor,
        )

        self.results.append(result)

        return result

    def best_by_profit_factor(self) -> Optional[ExperimentResult]:
        """
        Return the experiment with the highest profit factor.
        """

        if not self.results:
            return None

        return max(
            self.results,
            key=lambda result: result.profit_factor,
        )

    def best_by_net_profit(self) -> Optional[ExperimentResult]:
        """
        Return the experiment with the highest net profit.
        """

        if not self.results:
            return None

        return max(
            self.results,
            key=lambda result: result.net_profit,
        )

    def profitable_results(self) -> List[ExperimentResult]:
        """
        Return experiments that produced positive net profit.
        """

        return [
            result
            for result in self.results
            if result.net_profit > 0
        ]
