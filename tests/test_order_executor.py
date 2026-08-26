from app.broker.order_executor import OrderExecutor


def test_order_executor_creation():

    executor = OrderExecutor()

    assert executor is not None