import ta
import talib
import pandas_ta as pta
import pandas as pd

OSCILLATORS = pd.DataFrame(
    {
        #   "osc" : (tuple/function: function(s), tuple: (parts of df), tuple: (default param values), bool: relative to closing price)
        # Awesome Oscillator: above and below 0
        "ao": (ta.momentum.awesome_oscillator, ("high", "low"), (5, 34), False),
        # Relative Strength Index: 0-100
        "rsi": (ta.momentum.rsi, ("close",), (14,), False),
        # Stochastic Oscillator: 0-100
        "stoch": (ta.momentum.stoch, ("high", "low", "close"), (14, 3), False),
        # True strength index: (-100)-100
        "tsi": (ta.momentum.tsi, ("close",), (25, 13), False),
        # Ultimate Oscillator: 0-100
        "uo": (
            ta.momentum.ultimate_oscillator,
            ("high", "low", "close"),
            (7, 14, 28, 4.0, 2.0, 1.0),
            False,
        ),
        # Kaufman’s Adaptive Moving Average: Overlay
        "kama": (ta.momentum.kama, ("close",), (10, 2, 30), True),
        # Accumulation/Distribution Index: Large positive values
        # "adi": (ta.volume.acc_dist_index, ("high", "low", "close", "volume"), (), False),
        # Chaikin Money Flow: above and below 0
        "cmf": (
            ta.volume.chaikin_money_flow,
            ("high", "low", "close", "volume"),
            (20,),
            False,
        ),
        # Force Index: above and below 0 (many digits)
        "fi": (ta.volume.force_index, ("close", "volume"), (13,), False),
        # Money Flow Index: 0-100
        "mfi": (
            ta.volume.money_flow_index,
            ("high", "low", "close", "volume"),
            (14,),
            False,
        ),
        # Negative Volume Index
        "nvi": (ta.volume.negative_volume_index, ("close", "volume"), (), False),
        # On-balance volume: above and below 0 (many digits)
        # "obv": (ta.volume.on_balance_volume, ("close", "volume"), (), False),
        # Volume-price trend: Large positive values
        # "vpt": (ta.volume.volume_price_trend, ("close", "volume"), (), False),
        # Bollinger Bands: Overlays
        "boll": (
            (ta.volatility.bollinger_hband, ta.volatility.bollinger_lband),
            ("close",),
            (20, 2),
            True,
        ),
        # Donchian Channel: Overlays
        "dc": (
            (
                ta.volatility.donchian_channel_hband,
                ta.volatility.donchian_channel_lband,
            ),
            ("high", "low", "close"),
            (20, 0),
            True,
        ),
        # Keltner Channel: Overlays
        "kc": (
            (ta.volatility.keltner_channel_hband, ta.volatility.keltner_channel_lband),
            ("high", "low", "close"),
            (20, 0),
            True,
        ),
        # Average Directional Movement Index: 0-100
        "adx": (
            (ta.trend.adx, ta.trend.adx_pos, ta.trend.adx_neg),
            ("high", "low", "close"),
            (14,),
            False,
        ),
        # Exponential Moving Average: Overlay
        "ema": (ta.trend.ema_indicator, ("close",), (14,), True),
        # Simple Moving Average: Overlay
        "sma": (ta.trend.sma_indicator, ("close",), (14,), True),
        # Ichimoku Kinkō Hyō Senkou Span A: Overlay
        # "ichi": ((ta.trend.ichimoku_a, ta.trend.ichimoku_b), ("high", "low"), (9, 26, 52), True),
        # Know Sure Thing Oscillator: above and below 0
        # "kst": (ta.trend.kst, ("close",), (10, 15, 20, 30, 10, 10, 10, 15, 9), False),
        # Moving Average Convergence Divergence: above and below 0
        "macd": (ta.trend.macd_diff, ("close",), (26, 12, 9), True),
        # Mass Index: 0-100
        "mi": (ta.trend.mass_index, ("high", "low"), (9, 25), False),
        # KDJ
        "kdj": (pta.kdj, ("high", "low", "close"), (9, 3), False),
        # Psychological Line
        # "psl": (pta.psl, ("close", "open"), (12,), False),
        # Fibonacci's Weighted Moving Average
        # "fwma": (pta.fwma, ("close",), (10,), True),
        # Hull Exponential Moving Average
        # "hma": (pta.hma, ("close",), (10,), True),
        # Pascal's Weighted Moving Average
        # "pwma": (pta.pwma, ("close",), (10,), True),
        # Supertrend
        # "st": (pta.supertrend, ("high", "low", "close"), (7,), True),
        # Zero Lag Moving Average
        # "zlma": (pta.zlma, ("close",), (10,), True),
        # Entropy
        "entropy": (pta.entropy, ("close",), (10, 2), False),
        # Kurtosis
        "kurtosis": (pta.kurtosis, ("close",), (30,), False),
        # Skew
        "skew": (pta.skew, ("close",), (30,), False),
        # Standard Deviation
        "stdev": (pta.stdev, ("close",), (30,), True),
        # Z Score
        # "zs": (pta.zscore, ("close",), (30,), False),
        # Choppiness Index
        # "chop": (pta.chop, ("high", "low", "close"), (14,), False),
        # Chande Kroll Stop
        # "cksp": (pta.cksp, ("high", "low", "close"), (10, 1, 9), False),
        # Linear Decay:
        # "ld": (pta.linear_decay, ("close",), (1,), False),
        # Q Stick
        # "qs": (pta.qstick, ("open", "close"), (1,), False),
        # Aberration
        # "aberration": (pta.aberration, ("high", "low", "close"), (5, 15), False),
        # Acceleration Bands
        # "ab": (pta.accbands, ("high", "low", "close"), (10, 4), True),
        # Relative Volatility Index
        # "rvi": (pta.rvi, ("open", "high", "low", "close"), (14, 4), False),
        # Elder's Force Index
        # "efi": (pta.efi, ("close", "volume"), (13,), False),
        # Ease of Movement
        # "eom": (pta.eom, ("high", "low", "close", "volume"), (14,), False),
        # Positive Volume Index
        # "pvi": (pta.pvi, ("close", "volume"), (13, 1000), False),
        # Price - Volume
        "pvol": (pta.pvol, ("close", "volume"), (), False),
        # Volume Profile
        # "vp": (pta.vp, ("close", "volume"), (10,), False)
    }
).T

OSCILLATORS.columns = ["function", "columns", "params", "relative"]

SUFFIXES = {
    "boll": ("h", "l"),
    "dc": ("h", "l"),
    "kc": ("h", "l"),
    "adx": ("", "p", "n"),
    "ichi": ("a", "b"),
    "cksp": ("l", "s"),
    "br": ("ar", "br"),
    "kdj": ("l", "", "m"),
    "ab": ("l", "m", "u"),
}

OSCILLATORS["suffixes"] = [
    SUFFIXES[osc] if osc in SUFFIXES.keys() else ("",) for osc in OSCILLATORS.index
]


PATTERNS = {
    # Three Inside Up/Down
    "cdl3inside": talib.CDL3INSIDE,
    # Three Outside Up/Down
    "cdl3outside": talib.CDL3OUTSIDE,
    # Three Stars In The South
    "cdl3starsinsouth": talib.CDL3STARSINSOUTH,
    # Three Advancing White Soldiers
    "cdl3whitesoldiers": talib.CDL3WHITESOLDIERS,
    # Breakaway
    "cdlbreakaway": talib.CDLBREAKAWAY,
    # Counterattack
    "cdlcounterattack": talib.CDLCOUNTERATTACK,
    # Doji Star
    "cdldojistar": talib.CDLDOJISTAR,
    # Dragonfly Doji
    "cdldragonflydoji": talib.CDLDRAGONFLYDOJI,
    # Engulfing Pattern
    "cdlengulfing": talib.CDLENGULFING,
    # Hammer
    "cdlhammer": talib.CDLHAMMER,
    # Homing Pigeon
    "cdlhomingpigeon": talib.CDLHOMINGPIGEON,
    # Inverted Hammer
    "cdlinvertedhammer": talib.CDLINVERTEDHAMMER,
    # Ladder Bottom
    "cdlladderbottom": talib.CDLLADDERBOTTOM,
    # Long Line Candle
    "cdllongline": talib.CDLLONGLINE,
    # Marubozu
    "cdlmarubozu": talib.CDLMARUBOZU,
    # Matching Low
    "cdlmatchinglow": talib.CDLMATCHINGLOW,
    # Morning Doji Star
    "cdlmorningdojistar": talib.CDLMORNINGDOJISTAR,
    # On-Neck Pattern
    "cdlonneck": talib.CDLONNECK,
    # Piercing Pattern
    "cdlpiercing": talib.CDLPIERCING,
    # Separating Lines
    "cdlseparatinglines": talib.CDLSEPARATINGLINES,
    # Thrusting Pattern
    "cdlthrusting": talib.CDLTHRUSTING,
    # Tristar Pattern
    "cdltristar": talib.CDLTRISTAR,
    # Unique 3 River
    "cdlunique3river": talib.CDLUNIQUE3RIVER,
    # Upside/Downside Gap Three Methods
    "cdlxsidegap3methods": talib.CDLXSIDEGAP3METHODS,
}
