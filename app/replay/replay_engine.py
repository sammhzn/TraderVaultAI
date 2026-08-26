from app.strategy.strategy_engine import StrategyEngine


class ReplayEngine:

    def __init__(self):

        self.strategy = StrategyEngine()

    def replay(self, market_contexts):

        decisions = []

        for context in market_contexts:

            decision = self.strategy.evaluate(context)

            decisions.append(decision)

        return decisions