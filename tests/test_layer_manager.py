from app.strategy.layer_manager import LayerManager


def test_buy_layer():

    manager = LayerManager()

    result = manager.should_add_layer(
        direction="BUY",
        first_entry=4080.00,
        current_price=4079.80,
        current_layers=1,
    )

    assert result.add_layer
    assert result.layer_number == 2


def test_sell_layer():

    manager = LayerManager()

    result = manager.should_add_layer(
        direction="SELL",
        first_entry=4080.00,
        current_price=4080.20,
        current_layers=1,
    )

    assert result.add_layer
    assert result.layer_number == 2


def test_max_layers():

    manager = LayerManager()

    result = manager.should_add_layer(
        direction="BUY",
        first_entry=4080.00,
        current_price=4079.00,
        current_layers=5,
    )

    assert not result.add_layer