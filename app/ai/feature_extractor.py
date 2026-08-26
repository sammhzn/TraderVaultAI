from datetime import datetime
import math

from app.indicators.ema import EMAIndicator
from app.indicators.rsi import RSIIndicator
from app.indicators.atr import ATRIndicator
from app.indicators.macd import MACDIndicator
from app.indicators.adx import ADXIndicator
from app.indicators.bollinger import BollingerBandsIndicator
from app.ai.market_regime import MarketRegimeDetector


class FeatureExtractor:

    def __init__(self):

        self.ema = EMAIndicator()
        self.rsi = RSIIndicator()
        self.atr = ATRIndicator()
        self.macd = MACDIndicator()
        self.adx = ADXIndicator()
        self.bollinger = BollingerBandsIndicator()

        self.regime_detector = MarketRegimeDetector()

    def _candles_until_trade(self, candles, trade_time):
        """
        Return only candles that were available when the trade opened.

        This prevents future candles from leaking into the AI dataset.
        """

        if not candles or not isinstance(trade_time, datetime):
            return []

        filtered = []

        for candle in candles:

            try:
                candle_time = datetime.fromtimestamp(
                    candle["time"]
                )
            except (KeyError, TypeError, ValueError):
                continue

            if candle_time <= trade_time:
                filtered.append(candle)

        return filtered

    def _valid_number(self, value):
        """
        Check whether an indicator value is usable.
        """

        if value is None:
            return False

        try:
            return math.isfinite(float(value))
        except (TypeError, ValueError):
            return False

    def _safe_divide(self, numerator, denominator):
        """
        Safely divide two numeric values.

        Returns None when the denominator is zero or either
        value is invalid.
        """

        if not self._valid_number(numerator):
            return None

        if not self._valid_number(denominator):
            return None

        denominator = float(denominator)

        if denominator == 0:
            return None

        return float(numerator) / denominator

    def extract(
        self,
        symbol,
        strategy,
        trade,
        previous_day_high,
        previous_day_low,
        candles=None,
    ):

        open_time = trade.open_time

        if isinstance(open_time, datetime):

            trade_date = open_time.date().isoformat()
            hour = open_time.hour
            day = open_time.strftime("%A")

        else:

            trade_date = None
            hour = None
            day = None

        features = {
            "symbol": symbol,
            "strategy": strategy,
            "direction": trade.direction,
            "entry": trade.entry,
            "stop_loss": trade.stop_loss,
            "take_profit": trade.take_profit,
            "layer": trade.layer,
            "previous_day_high": previous_day_high,
            "previous_day_low": previous_day_low,

            "open_time": (
                trade.open_time.isoformat()
                if isinstance(trade.open_time, datetime)
                else None
            ),

            "close_time": (
                trade.close_time.isoformat()
                if isinstance(trade.close_time, datetime)
                else None
            ),
            
            "trade_date": trade_date,
            "hour": hour,
            "day": day,
            "profit": trade.profit,
            "result": trade.result,
        }

        # --------------------------------------------------
        # Point-in-time candle filtering
        # --------------------------------------------------

        historical_candles = self._candles_until_trade(
            candles,
            open_time,
        )

        # --------------------------------------------------
        # Technical indicators
        # --------------------------------------------------

        if historical_candles:

            ema20 = self.ema.calculate(
                historical_candles,
                period=20,
            )

            ema50 = self.ema.calculate(
                historical_candles,
                period=50,
            )

            rsi = self.rsi.calculate(
                historical_candles,
                period=14,
            )

            atr = self.atr.calculate(
                historical_candles,
                period=14,
            )

            macd = self.macd.calculate(
                historical_candles
            )

            adx = self.adx.calculate(
                historical_candles,
                period=14,
            )

            bollinger = self.bollinger.calculate(
                historical_candles,
                period=20,
            )

            # Latest candle available at trade entry.
            index = -1

            ema20_value = ema20[index]
            ema50_value = ema50[index]

            rsi_value = rsi[index]

            atr_value = atr[index]

            macd_value = macd["macd"][index]
            macd_signal_value = macd["signal"][index]
            macd_histogram_value = macd["histogram"][index]

            adx_value = adx["adx"][index]
            plus_di_value = adx["plus_di"][index]
            minus_di_value = adx["minus_di"][index]

            bollinger_middle_value = bollinger["middle"][index]
            bollinger_upper_value = bollinger["upper"][index]
            bollinger_lower_value = bollinger["lower"][index]
            bollinger_width_value = bollinger["width"][index]

            # --------------------------------------------------
            # Market regime
            # --------------------------------------------------

            regime = {
                "regime": None,
                "trend": None,
                "trend_strength": None,
                "momentum": None,
                "directional_bias": None,
            }

            if (
                self._valid_number(ema20_value)
                and self._valid_number(ema50_value)
                and self._valid_number(rsi_value)
                and self._valid_number(atr_value)
                and self._valid_number(adx_value)
                and self._valid_number(plus_di_value)
                and self._valid_number(minus_di_value)
            ):

                regime = self.regime_detector.detect(
                    ema20=ema20_value,
                    ema50=ema50_value,
                    rsi=rsi_value,
                    atr=atr_value,
                    adx=adx_value,
                    plus_di=plus_di_value,
                    minus_di=minus_di_value,
                )

            # --------------------------------------------------
            # Normalized / scale-independent features
            # --------------------------------------------------

            # Distance from previous-day levels expressed in ATRs.
            distance_from_pdh = (
                trade.entry - previous_day_high
                if self._valid_number(previous_day_high)
                else None
            )

            distance_from_pdl = (
                trade.entry - previous_day_low
                if self._valid_number(previous_day_low)
                else None
            )

            entry_distance_from_pdh_atr = self._safe_divide(
                distance_from_pdh,
                atr_value,
            )

            entry_distance_from_pdl_atr = self._safe_divide(
                distance_from_pdl,
                atr_value,
            )

            # EMA spread relative to current volatility.
            ema_spread = None

            if (
                self._valid_number(ema20_value)
                and self._valid_number(ema50_value)
            ):
                ema_spread = (
                    ema20_value - ema50_value
                )

            ema_spread_atr = self._safe_divide(
                ema_spread,
                atr_value,
            )

            # Trade risk and reward normalized by ATR.
            risk_distance = abs(
                trade.entry - trade.stop_loss
            )

            reward_distance = abs(
                trade.take_profit - trade.entry
            )

            risk_atr = self._safe_divide(
                risk_distance,
                atr_value,
            )

            reward_atr = self._safe_divide(
                reward_distance,
                atr_value,
            )

            # Reward/risk ratio.
            reward_risk_ratio = self._safe_divide(
                reward_distance,
                risk_distance,
            )

            # MACD histogram relative to ATR.
            macd_histogram_atr = self._safe_divide(
                macd_histogram_value,
                atr_value,
            )

            # Bollinger width relative to ATR.
            bollinger_width_atr = self._safe_divide(
                bollinger_width_value,
                atr_value,
            )

            # Position of entry within the Bollinger structure.
            bollinger_position = None

            if (
                self._valid_number(bollinger_upper_value)
                and self._valid_number(bollinger_lower_value)
            ):

                band_range = (
                    bollinger_upper_value
                    - bollinger_lower_value
                )

                if band_range != 0:

                    bollinger_position = (
                        trade.entry
                        - bollinger_lower_value
                    ) / band_range

            # DI spread and normalized DI spread.
            di_spread = None

            if (
                self._valid_number(plus_di_value)
                and self._valid_number(minus_di_value)
            ):

                di_spread = (
                    plus_di_value
                    - minus_di_value
                )

            # --------------------------------------------------
            # Original + normalized features
            # --------------------------------------------------

            features.update({

                # EMA
                "ema20": ema20_value,
                "ema50": ema50_value,

                # RSI
                "rsi": rsi_value,

                # ATR
                "atr": atr_value,

                # MACD
                "macd": macd_value,
                "macd_signal": macd_signal_value,
                "macd_histogram": macd_histogram_value,

                # ADX / directional movement
                "adx": adx_value,
                "plus_di": plus_di_value,
                "minus_di": minus_di_value,

                # Bollinger Bands
                "bollinger_middle": bollinger_middle_value,
                "bollinger_upper": bollinger_upper_value,
                "bollinger_lower": bollinger_lower_value,
                "bollinger_width": bollinger_width_value,

                # Market regime
                "market_regime": regime["regime"],
                "trend": regime["trend"],
                "trend_strength": regime["trend_strength"],
                "momentum": regime["momentum"],
                "directional_bias": regime["directional_bias"],

                # --------------------------------------------------
                # Normalized features
                # --------------------------------------------------

                "entry_distance_from_pdh_atr":
                    entry_distance_from_pdh_atr,

                "entry_distance_from_pdl_atr":
                    entry_distance_from_pdl_atr,

                "ema_spread":
                    ema_spread,

                "ema_spread_atr":
                    ema_spread_atr,

                "risk_distance":
                    risk_distance,

                "reward_distance":
                    reward_distance,

                "risk_atr":
                    risk_atr,

                "reward_atr":
                    reward_atr,

                "reward_risk_ratio":
                    reward_risk_ratio,

                "macd_histogram_atr":
                    macd_histogram_atr,

                "bollinger_width_atr":
                    bollinger_width_atr,

                "bollinger_position":
                    bollinger_position,

                "di_spread":
                    di_spread,
            })

        else:

            # Keep extractor backward compatible.

            features.update({

                "ema20": None,
                "ema50": None,

                "rsi": None,

                "atr": None,

                "macd": None,
                "macd_signal": None,
                "macd_histogram": None,

                "adx": None,
                "plus_di": None,
                "minus_di": None,

                "bollinger_middle": None,
                "bollinger_upper": None,
                "bollinger_lower": None,
                "bollinger_width": None,

                "market_regime": None,
                "trend": None,
                "trend_strength": None,
                "momentum": None,
                "directional_bias": None,

                # Normalized features
                "entry_distance_from_pdh_atr": None,
                "entry_distance_from_pdl_atr": None,
                "ema_spread": None,
                "ema_spread_atr": None,
                "risk_distance": None,
                "reward_distance": None,
                "risk_atr": None,
                "reward_atr": None,
                "reward_risk_ratio": None,
                "macd_histogram_atr": None,
                "bollinger_width_atr": None,
                "bollinger_position": None,
                "di_spread": None,
            })

        return features