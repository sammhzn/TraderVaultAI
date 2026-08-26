from app.strategy.daily_levels import DailyLevelEngine


def test_update_levels():
    engine = DailyLevelEngine()

    engine.update_level("previous_day_high", 4080.50)

    assert engine.get_levels().previous_day_high == 4080.50


def test_update_current_day_low():
    engine = DailyLevelEngine()

    engine.update_level("current_day_low", 4069.20)

    assert engine.get_levels().current_day_low == 4069.20