# indicators.py

import pandas as pd
import talib


# 1. Moving Average Crossovers with RSI Confirmation
def add_ema_crossover_with_rsi(
    df: pd.DataFrame, fast_period: int = 5, slow_period: int = 12, rsi_period: int = 7
):
    """Adds Fast and Slow EMA crossovers with RSI confirmation."""
    df["fast_ema"] = talib.EMA(df["close"], timeperiod=fast_period)
    df["slow_ema"] = talib.EMA(df["close"], timeperiod=slow_period)
    df["rsi"] = talib.RSI(df["close"], timeperiod=rsi_period)
    return df


# 2. Bollinger Bands with Stochastic Oscillator for Reversals
def add_bollinger_bands_with_stochastic(
    df: pd.DataFrame,
    bb_window: int = 20,
    multiplier: float = 2,
    stoch_fastk_period: int = 5,
    stoch_fastd_period: int = 3,
):
    """Adds Bollinger Bands and Stochastic Oscillator for reversal detection."""
    upper_band, middle_band, lower_band = talib.BBANDS(
        df["close"], timeperiod=bb_window, nbdevup=multiplier, nbdevdn=multiplier
    )
    df["upper_band"], df["middle_band"], df["lower_band"] = (
        upper_band,
        middle_band,
        lower_band,
    )
    df["stoch_k"], df["stoch_d"] = talib.STOCHF(
        df["high"],
        df["low"],
        df["close"],
        fastk_period=stoch_fastk_period,
        fastd_period=stoch_fastd_period,
    )
    return df


# 3. MACD with Parabolic SAR for Trend-Momentum Combination
def add_macd_with_parabolic_sar(
    df: pd.DataFrame,
    fast_period: int = 5,
    slow_period: int = 13,
    signal_period: int = 1,
):
    """Adds MACD and Parabolic SAR for trend and momentum combination."""
    macd, signal, hist = talib.MACD(
        df["close"],
        fastperiod=fast_period,
        slowperiod=slow_period,
        signalperiod=signal_period,
    )
    df["macd"], df["macd_signal"], df["macd_hist"] = macd, signal, hist
    df["parabolic_sar"] = talib.SAR(
        df["high"], df["low"], acceleration=0.02, maximum=0.2
    )
    return df


# 4. ATR with VWAP for Volume and Volatility-Based Entries
def add_atr_with_vwap(df: pd.DataFrame, atr_period: int = 7):
    """Adds ATR and VWAP for entries based on volume and volatility."""
    df["atr"] = talib.ATR(df["high"], df["low"], df["close"], timeperiod=atr_period)
    # VWAP requires volume; calculation here assumes columns 'close', 'volume', and time-weighted average.
    df["vwap"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
    return df


# 5. Scalping with EMA and MFI for Momentum-Volume Confirmation
def add_ema_with_mfi(df: pd.DataFrame, ema_period: int = 8, mfi_period: int = 7):
    """Adds EMA and MFI for scalping strategy."""
    df["ema"] = talib.EMA(df["close"], timeperiod=ema_period)
    df["mfi"] = talib.MFI(
        df["high"], df["low"], df["close"], df["volume"], timeperiod=mfi_period
    )
    return df


# 6. VWAP, RSI, and ATR Filter for Noise Reduction in Volatile Markets
def add_vwap_rsi_atr_filter(df: pd.DataFrame, rsi_period: int = 7, atr_period: int = 7):
    """Adds VWAP, RSI, and ATR for noise reduction."""
    df["vwap"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
    df["rsi"] = talib.RSI(df["close"], timeperiod=rsi_period)
    df["atr"] = talib.ATR(df["high"], df["low"], df["close"], timeperiod=atr_period)
    return df


# 7. ATR for Volatility
def add_atr(df: pd.DataFrame, period: int = 14):
    """Adds ATR (Average True Range) to the DataFrame for measuring volatility."""
    if not {"high", "low", "close"}.issubset(df.columns):
        raise ValueError("DataFrame must contain 'high', 'low', and 'close' columns.")

    df["atr"] = talib.ATR(df["high"], df["low"], df["close"], timeperiod=period)
    return df
