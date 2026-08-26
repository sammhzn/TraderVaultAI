from app.broker.mt5_connector import MT5Connector


def test_connector_creation():

    connector = MT5Connector()

    assert connector is not None