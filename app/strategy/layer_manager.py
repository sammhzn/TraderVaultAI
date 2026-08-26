from dataclasses import dataclass


@dataclass
class LayerDecision:
    add_layer: bool
    layer_number: int
    entry_price: float
    reason: str


class LayerManager:

    def should_add_layer(
        self,
        direction: str,
        first_entry: float,
        current_price: float,
        current_layers: int,
        spacing: float = 0.20,
        preferred_layers: int = 3,
        maximum_layers: int = 5,
    ) -> LayerDecision:

        if current_layers >= maximum_layers:
            return LayerDecision(
                False,
                current_layers,
                current_price,
                "Maximum layers reached",
            )

        next_layer_price = (
            first_entry - (current_layers * spacing)
            if direction == "BUY"
            else first_entry + (current_layers * spacing)
        )

        if direction == "BUY" and current_price <= next_layer_price:
            return LayerDecision(
                True,
                current_layers + 1,
                current_price,
                "BUY pullback layer",
            )

        if direction == "SELL" and current_price >= next_layer_price:
            return LayerDecision(
                True,
                current_layers + 1,
                current_price,
                "SELL pullback layer",
            )

        return LayerDecision(
            False,
            current_layers,
            current_price,
            "No new layer",
        )