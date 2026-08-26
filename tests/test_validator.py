from app.strategy.validator import StrategyValidator


def test_valid_trade():

    validator = StrategyValidator()

    result = validator.validate(
        liquidity_valid=True,
        signal_valid=True,
        entry_valid=True,
        pullback_valid=True,
    )

    assert result.valid is True
    assert result.action == "EXECUTE"


def test_invalid_trade():

    validator = StrategyValidator()

    result = validator.validate(
        liquidity_valid=False,
        signal_valid=True,
        entry_valid=True,
        pullback_valid=True,
    )

    assert result.valid is False
    assert result.action == "NO TRADE"