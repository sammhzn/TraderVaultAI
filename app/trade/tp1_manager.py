class TP1Manager:

    def manage(
        self,
        simulator,
        close_layers=2,
    ):

        simulator.close_newest_layers(
            count=close_layers,
        )

        simulator.move_to_break_even()

        return simulator.active_trades()