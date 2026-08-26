from dataclasses import dataclass
from itertools import product
from typing import Any, Dict, List, Optional


@dataclass
class ParameterCombination:
    """
    Represents one combination of strategy parameters.
    """

    parameters: Dict[str, Any]


class ParameterSearch:
    """
    Generates every possible combination of supplied
    strategy parameters.

    Example:

        {
            "rsi_period": [10, 14],
            "rr": [2, 4]
        }

    produces:

        1. rsi_period=10, rr=2
        2. rsi_period=10, rr=4
        3. rsi_period=14, rr=2
        4. rsi_period=14, rr=4
    """

    def __init__(
        self,
        parameters: Optional[
            Dict[str, List[Any]]
        ] = None,
    ):
        self.parameters = parameters or {}

    def generate(
        self,
    ) -> List[ParameterCombination]:
        """
        Generate all possible parameter combinations.
        """

        if not self.parameters:
            return []

        names = list(
            self.parameters.keys()
        )

        values = [
            self.parameters[name]
            for name in names
        ]

        combinations = []

        for combination in product(*values):

            parameters = dict(
                zip(
                    names,
                    combination,
                )
            )

            combinations.append(
                ParameterCombination(
                    parameters=parameters
                )
            )

        return combinations

    def count(self) -> int:
        """
        Return the number of combinations that
        will be generated.
        """

        if not self.parameters:
            return 0

        total = 1

        for values in self.parameters.values():
            total *= len(values)

        return total

    def set_parameters(
        self,
        parameters: Dict[str, List[Any]],
    ) -> None:
        """
        Replace the current parameter search space.
        """

        self.parameters = parameters

    def parameter_names(self) -> List[str]:
        """
        Return the names of parameters being searched.
        """

        return list(
            self.parameters.keys()
        )