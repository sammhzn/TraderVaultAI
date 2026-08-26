from app.engine.trading_engine import TradingEngine


def test_engine_creation():

    engine = TradingEngine()

    assert engine is not None