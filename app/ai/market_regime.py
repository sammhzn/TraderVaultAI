class MarketRegimeDetector:

    def detect(
        self,
        ema20,
        ema50,
        rsi,
        atr,
        adx,
        plus_di,
        minus_di,
    ):

        # -----------------------------
        # Trend direction
        # -----------------------------

        if ema20 > ema50:
            trend = "BULLISH"

        elif ema20 < ema50:
            trend = "BEARISH"

        else:
            trend = "RANGING"

        # -----------------------------
        # Trend strength
        # -----------------------------

        if adx >= 25:
            trend_strength = "STRONG"

        elif adx >= 20:
            trend_strength = "MODERATE"

        else:
            trend_strength = "WEAK"

        # -----------------------------
        # RSI momentum
        # -----------------------------

        if rsi >= 70:
            momentum = "OVERBOUGHT"

        elif rsi <= 30:
            momentum = "OVERSOLD"

        elif rsi >= 55:
            momentum = "BULLISH"

        elif rsi <= 45:
            momentum = "BEARISH"

        else:
            momentum = "NEUTRAL"

        # -----------------------------
        # Directional pressure
        # -----------------------------

        if plus_di > minus_di:
            directional_bias = "BUYERS"

        elif minus_di > plus_di:
            directional_bias = "SELLERS"

        else:
            directional_bias = "BALANCED"

        # -----------------------------
        # Overall market regime
        # -----------------------------

        if trend == "BULLISH" and trend_strength == "STRONG":
            regime = "STRONG_BULLISH"

        elif trend == "BEARISH" and trend_strength == "STRONG":
            regime = "STRONG_BEARISH"

        elif trend == "BULLISH":
            regime = "WEAK_BULLISH"

        elif trend == "BEARISH":
            regime = "WEAK_BEARISH"

        else:
            regime = "RANGING"

        return {
            "regime": regime,
            "trend": trend,
            "trend_strength": trend_strength,
            "momentum": momentum,
            "directional_bias": directional_bias,
            "atr": atr,
        }