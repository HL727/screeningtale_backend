from app.db.base import Base
from sqlalchemy import Column, String, Float, DateTime, Integer


class Historical(Base):
    __tablename__ = "historical"
    date = Column(DateTime, primary_key=True, index=True)
    growth = Column(Float, index=True)
    country = Column(String, index=True)
    ticker = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    industry = Column(String, index=True)
    sector = Column(String, index=True)
    close = Column(Float, index=True)
    change_percent = Column(Float, index=True)
    volume = Column(Float, index=True)
    turnover_percent = Column(Float, index=True)
    range_percent = Column(Float, index=True)
    year_high_rel = Column(Float, index=True)
    year_low_rel = Column(Float, index=True)
    market_cap = Column(Float, index=True)
    market_cap_usd = Column(Float, index=True)
    eps = Column(Float, index=True)
    dps = Column(Float, index=True)
    dividend_yield_percent = Column(Float, index=True)
    book_value = Column(Float, index=True)
    pb = Column(Float, index=True)
    ps = Column(Float, index=True)
    pe = Column(Float, index=True)
    peg = Column(Float, index=True)
    pcf = Column(Float, index=True)
    evs = Column(Float, index=True)
    evebitda = Column(Float, index=True)
    evebit = Column(Float, index=True)
    evnopat = Column(Float, index=True)
    ebitda_margin = Column(Float, index=True)
    ebit_margin = Column(Float, index=True)
    profit_margin = Column(Float, index=True)
    revenue_5y_cagr = Column(Float, index=True)
    ebitda_5y_cagr = Column(Float, index=True)
    ebit_5y_cagr = Column(Float, index=True)
    profit_5y_cagr = Column(Float, index=True)
    roe = Column(Float, index=True)
    roa = Column(Float, index=True)
    roce = Column(Float, index=True)
    roic = Column(Float, index=True)
    rod = Column(Float, index=True)
    current_ratio = Column(Float, index=True)
    quick_ratio = Column(Float, index=True)
    cash_ratio = Column(Float, index=True)
    ocf_ratio = Column(Float, index=True)
    wct = Column(Float, index=True)
    de = Column(Float, index=True)
    da = Column(Float, index=True)
    ea = Column(Float, index=True)
    piotroski = Column(Integer, index=True)
    altman_z = Column(Float, index=True)
    grade = Column(Float, index=True)
    ownership_percent = Column(Float, index=True)
    ownership_percent_change = Column(Float, index=True)
    put_call_ratio = Column(Float, index=True)
    put_call_ratio_change = Column(Float, index=True)
    ao = Column(Float, index=True)
    rsi = Column(Float, index=True)
    stoch = Column(Float, index=True)
    tsi = Column(Float, index=True)
    uo = Column(Float, index=True)
    cmf = Column(Float, index=True)
    fi = Column(Float, index=True)
    mfi = Column(Float, index=True)
    nvi = Column(Float, index=True)
    adx = Column(Float, index=True)
    adxp = Column(Float, index=True)
    adxn = Column(Float, index=True)
    macd = Column(Float, index=True)
    mi = Column(Float, index=True)
    kdj = Column(Float, index=True)
    pvol = Column(Float, index=True)
    stdev = Column(Float, index=True)
    entropy = Column(Float, index=True)
    skew = Column(Float, index=True)
    kurtosis = Column(Float, index=True)
    sma = Column(Float, index=True)
    ema = Column(Float, index=True)
    kama = Column(Float, index=True)
    bollh = Column(Float, index=True)
    bolll = Column(Float, index=True)
    dch = Column(Float, index=True)
    dcl = Column(Float, index=True)
    kch = Column(Float, index=True)
    kcl = Column(Float, index=True)
    days_since_bullish_cdlbreakaway = Column(Integer, index=True)
    days_since_bullish_cdlcounterattack = Column(Integer, index=True)
    days_since_bullish_cdldojistar = Column(Integer, index=True)
    days_since_bullish_cdldragonflydoji = Column(Integer, index=True)
    days_since_bullish_cdlengulfing = Column(Integer, index=True)
    days_since_bullish_cdlhammer = Column(Integer, index=True)
    days_since_bullish_cdlhomingpigeon = Column(Integer, index=True)
    days_since_bullish_cdlinvertedhammer = Column(Integer, index=True)
    days_since_bullish_cdlladderbottom = Column(Integer, index=True)
    days_since_bullish_cdllongline = Column(Integer, index=True)
    days_since_bullish_cdlmarubozu = Column(Integer, index=True)
    days_since_bullish_cdlmatchinglow = Column(Integer, index=True)
    days_since_bullish_cdlmorningdojistar = Column(Integer, index=True)
    days_since_bullish_cdlonneck = Column(Integer, index=True)
    days_since_bullish_cdlpiercing = Column(Integer, index=True)
    days_since_bullish_cdlseparatinglines = Column(Integer, index=True)
    days_since_bullish_cdl3whitesoldiers = Column(Integer, index=True)
    days_since_bullish_cdl3inside = Column(Integer, index=True)
    days_since_bullish_cdl3outside = Column(Integer, index=True)
    days_since_bullish_cdl3starsinsouth = Column(Integer, index=True)
    days_since_bullish_cdlthrusting = Column(Integer, index=True)
    days_since_bullish_cdltristar = Column(Integer, index=True)
    days_since_bullish_cdlunique3river = Column(Integer, index=True)
    days_since_bullish_cdlxsidegap3methods = Column(Integer, index=True)
    days_since_bearish_cdlcounterattack = Column(Integer, index=True)
    days_since_bearish_cdlbreakaway = Column(Integer, index=True)
    days_since_bearish_cdldojistar = Column(Integer, index=True)
    days_since_bearish_cdldragonflydoji = Column(Integer, index=True)
    days_since_bearish_cdlengulfing = Column(Integer, index=True)
    days_since_bearish_cdlhammer = Column(Integer, index=True)
    days_since_bearish_cdlhomingpigeon = Column(Integer, index=True)
    days_since_bearish_cdlinvertedhammer = Column(Integer, index=True)
    days_since_bearish_cdlladderbottom = Column(Integer, index=True)
    days_since_bearish_cdllongline = Column(Integer, index=True)
    days_since_bearish_cdlmarubozu = Column(Integer, index=True)
    days_since_bearish_cdlmatchinglow = Column(Integer, index=True)
    days_since_bearish_cdlmorningdojistar = Column(Integer, index=True)
    days_since_bearish_cdlonneck = Column(Integer, index=True)
    days_since_bearish_cdlpiercing = Column(Integer, index=True)
    days_since_bearish_cdlseparatinglines = Column(Integer, index=True)
    days_since_bearish_cdl3whitesoldiers = Column(Integer, index=True)
    days_since_bearish_cdl3inside = Column(Integer, index=True)
    days_since_bearish_cdl3outside = Column(Integer, index=True)
    days_since_bearish_cdl3starsinsouth = Column(Integer, index=True)
    days_since_bearish_cdlthrusting = Column(Integer, index=True)
    days_since_bearish_cdltristar = Column(Integer, index=True)
    days_since_bearish_cdlunique3river = Column(Integer, index=True)
    days_since_bearish_cdlxsidegap3methods = Column(Integer, index=True)
