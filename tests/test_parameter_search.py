from app.ai.parameter_search import (
    ParameterCombination,
    ParameterSearch,
)


def test_parameter_search_generates_all_combinations():

    search = ParameterSearch(
        {
            "rsi_period": [10, 14],
            "rr": [2, 4],
        }
    )

    combinations = search.generate()

    assert len(combinations) == 4


def test_parameter_search_generates_correct_values():

    search = ParameterSearch(
        {
            "rsi_period": [10, 14],
            "rr": [2, 4],
        }
    )

    combinations = search.generate()

    values = [
        combination.parameters
        for combination in combinations
    ]

    assert {
        "rsi_period": 10,
        "rr": 2,
    } in values

    assert {
        "rsi_period": 10,
        "rr": 4,
    } in values

    assert {
        "rsi_period": 14,
        "rr": 2,
    } in values

    assert {
        "rsi_period": 14,
        "rr": 4,
    } in values


def test_parameter_search_count():

    search = ParameterSearch(
        {
            "rsi_period": [7, 10, 14],
            "rr": [2, 3, 4, 5],
        }
    )

    assert search.count() == 12


def test_parameter_search_empty():

    search = ParameterSearch()

    assert search.generate() == []
    assert search.count() == 0


def test_parameter_names():

    search = ParameterSearch(
        {
            "rsi_period": [10, 14],
            "rr": [2, 4],
        }
    )

    assert search.parameter_names() == [
        "rsi_period",
        "rr",
    ]


def test_parameter_search_set_parameters():

    search = ParameterSearch()

    search.set_parameters(
        {
            "atr_multiplier": [0.5, 1.0],
            "rr": [2, 4],
        }
    )

    assert search.count() == 4