from app.services.market_data_service import MarketDataService


def test_market_service_creation():

    service = MarketDataService()

    assert service is not None