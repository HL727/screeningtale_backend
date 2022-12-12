import datetime
from typing import List, Optional

from pydantic import BaseModel


class HistoricalDate(BaseModel):
    date: datetime.date
    growth: Optional[float]

    class Config:
        orm_mode = True


class HistoricalDateReturn(BaseModel):
    date: datetime.date
    close: float

    class Config:
        orm_mode = True


class HistoricalPerformance(BaseModel):
    CAGR: float
    historical: List[HistoricalDateReturn]

    class Config:
        orm_mode = True


class MaxDateClass(BaseModel):
    MaxDate: datetime.date

    class Config:
        orm_mode = True


class Historical(BaseModel):
    date: Optional[datetime.date]
    growth: Optional[float]
    country: Optional[str]
    ticker: Optional[str]
    name: Optional[str]
    industry: Optional[str]
    sector: Optional[str]
    close: Optional[float]
    change_percent: Optional[float]
    volume: Optional[float]
    turnover_percent: Optional[float]
    range_percent: Optional[float]
    year_high_rel: Optional[float]
    year_low_rel: Optional[float]
    market_cap: Optional[float]
    market_cap_usd: Optional[float]
    eps: Optional[float]
    dps: Optional[float]
    dividend_yield_percent: Optional[float]
    book_value: Optional[float]
    pb: Optional[float]
    ps: Optional[float]
    pe: Optional[float]
    pcf: Optional[float]
    evs: Optional[float]
    evebitda: Optional[float]
    evebit: Optional[float]
    evnopat: Optional[float]
    ebitda_margin: Optional[float]
    ebit_margin: Optional[float]
    profit_margin: Optional[float]
    revenue_5y_cagr: Optional[float]
    ebitda_5y_cagr: Optional[float]
    ebit_5y_cagr: Optional[float]
    profit_5y_cagr: Optional[float]
    roe: Optional[float]
    roa: Optional[float]
    roce: Optional[float]
    roic: Optional[float]
    rod: Optional[float]
    current_ratio: Optional[float]
    quick_ratio: Optional[float]
    cash_ratio: Optional[float]
    ocf_ratio: Optional[float]
    wct: Optional[float]
    de: Optional[float]
    da: Optional[float]
    ea: Optional[float]
    piotroski: Optional[int]
    altman_z: Optional[float]
    grade: Optional[float]
    ownership_percent: Optional[float]
    ownership_percent_change: Optional[float]
    put_call_ratio: Optional[float]
    put_call_ratio_change: Optional[float]
    ao: Optional[float]
    rsi: Optional[float]
    stoch: Optional[float]
    tsi: Optional[float]
    uo: Optional[float]
    kama: Optional[float]
    cmf: Optional[float]
    fi: Optional[float]
    mfi: Optional[float]
    nvi: Optional[float]
    bollh: Optional[float]
    bolll: Optional[float]
    dch: Optional[float]
    dcl: Optional[float]
    kch: Optional[float]
    kcl: Optional[float]
    adx: Optional[float]
    adxp: Optional[float]
    adxn: Optional[float]
    ema: Optional[float]
    sma: Optional[float]
    macd: Optional[float]
    mi: Optional[float]
    kdj: Optional[float]
    entropy: Optional[float]
    kurtosis: Optional[float]
    skew: Optional[float]
    stdev: Optional[float]
    pvol: Optional[float]
    days_since_bearish_cdl2crows: Optional[int]
    days_since_bullish_cdl2crows: Optional[int]
    days_since_bearish_cdl3blackcrows: Optional[int]
    days_since_bullish_cdl3blackcrows: Optional[int]
    days_since_bearish_cdl3inside: Optional[int]
    days_since_bullish_cdl3inside: Optional[int]
    days_since_bearish_cdl3outside: Optional[int]
    days_since_bullish_cdl3outside: Optional[int]
    days_since_bearish_cdl3starsinsouth: Optional[int]
    days_since_bullish_cdl3starsinsouth: Optional[int]
    days_since_bearish_cdl3whitesoldiers: Optional[int]
    days_since_bullish_cdl3whitesoldiers: Optional[int]
    days_since_bearish_cdlabandonedbaby: Optional[int]
    days_since_bullish_cdlabandonedbaby: Optional[int]
    days_since_bearish_cdladvanceblock: Optional[int]
    days_since_bullish_cdladvanceblock: Optional[int]
    days_since_bearish_cdlbreakaway: Optional[int]
    days_since_bullish_cdlbreakaway: Optional[int]
    days_since_bearish_cdlcounterattack: Optional[int]
    days_since_bullish_cdlcounterattack: Optional[int]
    days_since_bearish_cdldoji: Optional[int]
    days_since_bullish_cdldoji: Optional[int]
    days_since_bearish_cdldojistar: Optional[int]
    days_since_bullish_cdldojistar: Optional[int]
    days_since_bearish_cdldragonflydoji: Optional[int]
    days_since_bullish_cdldragonflydoji: Optional[int]
    days_since_bearish_cdlengulfing: Optional[int]
    days_since_bullish_cdlengulfing: Optional[int]
    days_since_bearish_cdleveningdojistar: Optional[int]
    days_since_bullish_cdleveningdojistar: Optional[int]
    days_since_bearish_cdleveningstar: Optional[int]
    days_since_bullish_cdleveningstar: Optional[int]
    days_since_bearish_cdlgravestonedoji: Optional[int]
    days_since_bullish_cdlgravestonedoji: Optional[int]
    days_since_bearish_cdlhammer: Optional[int]
    days_since_bullish_cdlhammer: Optional[int]
    days_since_bearish_cdlhangingman: Optional[int]
    days_since_bullish_cdlhangingman: Optional[int]
    days_since_bearish_cdlhighwave: Optional[int]
    days_since_bullish_cdlhighwave: Optional[int]
    days_since_bearish_cdlhomingpigeon: Optional[int]
    days_since_bullish_cdlhomingpigeon: Optional[int]
    days_since_bearish_cdlidentical3crows: Optional[int]
    days_since_bullish_cdlidentical3crows: Optional[int]
    days_since_bearish_cdlinneck: Optional[int]
    days_since_bullish_cdlinneck: Optional[int]
    days_since_bearish_cdlinvertedhammer: Optional[int]
    days_since_bullish_cdlinvertedhammer: Optional[int]
    days_since_bearish_cdlladderbottom: Optional[int]
    days_since_bullish_cdlladderbottom: Optional[int]
    days_since_bearish_cdllongline: Optional[int]
    days_since_bullish_cdllongline: Optional[int]
    days_since_bearish_cdlmarubozu: Optional[int]
    days_since_bullish_cdlmarubozu: Optional[int]
    days_since_bearish_cdlmatchinglow: Optional[int]
    days_since_bullish_cdlmatchinglow: Optional[int]
    days_since_bearish_cdlmorningdojistar: Optional[int]
    days_since_bullish_cdlmorningdojistar: Optional[int]
    days_since_bearish_cdlmorningstar: Optional[int]
    days_since_bullish_cdlmorningstar: Optional[int]
    days_since_bearish_cdlonneck: Optional[int]
    days_since_bullish_cdlonneck: Optional[int]
    days_since_bearish_cdlpiercing: Optional[int]
    days_since_bullish_cdlpiercing: Optional[int]
    days_since_bearish_cdlrickshawman: Optional[int]
    days_since_bullish_cdlrickshawman: Optional[int]
    days_since_bearish_cdlseparatinglines: Optional[int]
    days_since_bullish_cdlseparatinglines: Optional[int]
    days_since_bearish_cdlshootingstar: Optional[int]
    days_since_bullish_cdlshootingstar: Optional[int]
    days_since_bearish_cdlspinningtop: Optional[int]
    days_since_bullish_cdlspinningtop: Optional[int]
    days_since_bearish_cdlstalledpattern: Optional[int]
    days_since_bullish_cdlstalledpattern: Optional[int]
    days_since_bearish_cdlthrusting: Optional[int]
    days_since_bullish_cdlthrusting: Optional[int]
    days_since_bearish_cdltristar: Optional[int]
    days_since_bullish_cdltristar: Optional[int]
    days_since_bearish_cdlunique3river: Optional[int]
    days_since_bullish_cdlunique3river: Optional[int]
    days_since_bearish_cdlupsidegap2crows: Optional[int]
    days_since_bullish_cdlupsidegap2crows: Optional[int]
    days_since_bearish_cdlxsidegap3methods: Optional[int]
    days_since_bullish_cdlxsidegap3methods: Optional[int]

    class Config:
        orm_mode = True


class TickersWithCriteria(BaseModel):
    results: List[Historical]
    count: int

    class Config:
        orm_mode = True
