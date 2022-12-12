import os
import sys
import pandas as pd
import numpy as np
import requests
import datetime

import asyncio
import aiohttp

from .columns import HISTORICAL_COLUMNS
from app.utils.countries import COUNTRY_CODES, CURRENCIES
from app.utils.make_dataset.technical import OSCILLATORS, PATTERNS, SUFFIXES
from app import schemas
from app.config import settings

import warnings

warnings.filterwarnings("ignore", category=Warning)

FMP_API_KEY = settings.FMP_API_KEY
FMP_API_BASE = settings.FMP_API_BASE

EXCHANGE_RATE_API_BASE = "https://api.exchangerate.host/"

DATA_FOLDER = "app/utils/make_dataset/data/"

CURRENCY_RATES = pd.DataFrame()
CURRENCY_DATE_SERIES = pd.Series()


async def get(url, session):
    async with session.get(url=url) as response:
        resp = await response.json()
        return resp
    # return requests.get(url)


async def send_requests_parallell(urls):
    async with aiohttp.ClientSession() as session:
        responses = await asyncio.gather(*[get(url, session) for url in urls.values()])
    # responses = [get(url, "test") for url in urls.values()]
    return {list(urls.keys())[i]: responses[i] for i in range(len(urls))}


async def update_currency_rates():
    currency_list = list(set(CURRENCIES.values()))
    today = datetime.datetime.now().date()
    dates = [
        datetime.date(year=y, month=m, day=1) - datetime.timedelta(days=1)
        for y in range(2010, today.year + 1)
        for m in range(1, 13)
        if (y < today.year) or (m <= today.month)
    ]
    urls = {
        date: f"{EXCHANGE_RATE_API_BASE}/{date}?base=USD&amount=1&symbols={','.join(currency_list)}"
        for date in dates
    }
    responses = await send_requests_parallell(urls)
    df = pd.DataFrame({key: val["rates"] for key, val in responses.items()}).T
    df.index = pd.to_datetime(df.index)
    df = df.fillna(method="ffill").fillna(method="bfill").fillna(1)
    # df.to_pickle(f"{DATA_FOLDER}/currency_rates.df")

    global CURRENCY_RATES
    global CURRENCY_DATE_SERIES

    CURRENCY_RATES = df.copy()
    CURRENCY_DATE_SERIES = pd.Series(df.index, index=df.index)


# Initialize currency rates data
asyncio.run(update_currency_rates())


def get_urls(ticker, years, buffer_years, is_usa):

    total_years = years + buffer_years
    total_quarters = int(np.ceil(4 * total_years))

    income_buffer_years = 6.5
    total_income_quarters = int(np.ceil(4 * (years + income_buffer_years)))

    from_date = str(
        (datetime.datetime.today() - datetime.timedelta(days=366 * total_years)).date()
    )

    urls = {
        "prices": f"{FMP_API_BASE}/v3/historical-price-full/{ticker}?from={from_date}&apikey={FMP_API_KEY}",
        "balance": f"{FMP_API_BASE}/v3/balance-sheet-statement/{ticker}?period=quarter&limit={total_quarters}&apikey={FMP_API_KEY}",
        "income": f"{FMP_API_BASE}/v3/income-statement/{ticker}?period=quarter&limit={total_income_quarters}&apikey={FMP_API_KEY}",
        "cashflow": f"{FMP_API_BASE}/v3/cash-flow-statement/{ticker}?period=quarter&limit={total_quarters}&apikey={FMP_API_KEY}",
        "dividend": f"{FMP_API_BASE}/v3/historical-price-full/stock_dividend/{ticker}?from={from_date}&apikey={FMP_API_KEY}",
        "profile": f"{FMP_API_BASE}/v3/profile/{ticker}?apikey={FMP_API_KEY}",
        "quote": f"{FMP_API_BASE}/v3/quote/{ticker}?apikey={FMP_API_KEY}",
    }

    if is_usa:
        urls = {
            **urls,
            **{
                "earnings_dates": f"{FMP_API_BASE}/v3/historical/earning_calendar/{ticker}?limit={max(total_quarters, total_income_quarters)}&apikey={FMP_API_KEY}",
                "ownership": f"{FMP_API_BASE}/v4/institutional-ownership/symbol-ownership?symbol={ticker}&includeCurrentQuarter=false&limit={total_quarters}&apikey={FMP_API_KEY}",
                "grades": f"{FMP_API_BASE}/v3/grade/{ticker}?apikey={FMP_API_KEY}",
            },
        }

    return urls


def get_price_data(prices_json, quote_json):
    prices = pd.DataFrame(prices_json["historical"]).iloc[::-1]

    if (prices["adjClose"] < 0).any():
        raise ValueError("Close prices can't be below 0")

    adj_cols = ["open", "high", "low"]
    prices[adj_cols] = prices[adj_cols].multiply(
        prices["adjClose"] / prices["close"], axis=0
    )

    prices = prices.loc[
        :, ["date", "adjClose", "open", "high", "low", "unadjustedVolume"]
    ]
    prices.rename(
        columns={"adjClose": "close", "unadjustedVolume": "volume"}, inplace=True
    )

    current_date = datetime.datetime.now().date()
    if current_date.weekday() > 4:
        current_date = current_date - datetime.timedelta(
            days=current_date.weekday() - 5
        )

    current_date_data = pd.Series(
        data=[str(current_date)]
        + [quote_json[0][c] for c in ["price", "open", "dayHigh", "dayLow", "volume"]],
        index=["date", "close", "open", "high", "low", "volume"],
    )

    if current_date_data["date"] != prices["date"].iloc[-1]:
        prices = prices.append(current_date_data, ignore_index=True)

    prices.index = pd.to_datetime(prices["date"])

    prices["change_percent"] = 100 * prices["close"].pct_change()
    prices["prev_close"] = prices["close"].shift(1)
    prices["range_percent"] = 100 * (
        2 * (prices["high"] - prices["low"]) / (prices["high"] + prices["low"])
    )

    return prices


def name(oscillator, parameters, suffix=""):
    if parameters == None or parameters == OSCILLATORS.loc[oscillator, "params"]:
        return oscillator
    temp = [str(num) if isinstance(num, int) else f"{num:.2f}" for num in parameters]
    return f"{oscillator}{suffix}({','.join(temp)})"


def get_columns(df, columns):
    return list(map(lambda c: df[c], columns))


def get_params(oscname):
    return [
        float(num) if "." in num else int(num)
        for num in oscname[oscname.index("(") + 1 : oscname.index(")")].split(",")
    ]


def osc_function(df, osc):
    if "(" in osc:
        oscname = osc[: osc.index("(")]
    else:
        oscname = osc
    has_suffix = False
    if oscname not in OSCILLATORS.index:
        suffix = oscname[-1]
        oscname = oscname[:-1]
        has_suffix = True

    args = get_columns(df, OSCILLATORS.loc[oscname, "columns"]) + list(
        OSCILLATORS.loc[oscname, "params"]
    )

    if has_suffix:
        index = OSCILLATORS.loc[oscname, "suffixes"].index(suffix)
        function = OSCILLATORS.loc[oscname, "function"][index]
    elif isinstance(OSCILLATORS.loc[oscname, "function"], tuple):
        function = OSCILLATORS.loc[oscname, "function"][0]
    else:
        function = OSCILLATORS.loc[oscname, "function"]
    result = function(*args)
    if OSCILLATORS.loc[oscname, "relative"]:
        result = 100 * (1 - result / df["close"])
    return result


def append_patterns(df):
    for pattern in PATTERNS.keys():
        is_pattern = PATTERNS[pattern](df["open"], df["high"], df["low"], df["close"])

        cum = (is_pattern >= 0).cumsum()
        df[f"days_since_bearish_{pattern}"] = cum - cum.where(is_pattern < 0).ffill()

        cum = (is_pattern <= 0).cumsum()
        df[f"days_since_bullish_{pattern}"] = cum - cum.where(is_pattern > 0).ffill()

    pattern_cols = [c for c in df if c.startswith("days_since_")]
    df[pattern_cols] = df[pattern_cols].fillna(365).clip(upper=365)
    return df


def get_oscs():
    oscs = []
    for osc in OSCILLATORS.index:
        if isinstance(OSCILLATORS.loc[osc, "function"], tuple):
            for suffix in OSCILLATORS.loc[osc, "suffixes"]:
                new_oscname = osc + suffix
                oscs.append(new_oscname)
        else:
            oscs.append(osc)
    return oscs


def append_extrema(df):
    roll = df["prev_close"].rolling("364d", min_periods=1)
    df[f"year_low"] = roll.min()
    df[f"year_high"] = roll.max()
    # df[f"days_since_year_low"] = 365 - roll.apply(np.argmin)
    # df[f"days_since_year_high"] = 365 - roll.apply(np.argmax)
    df[f"year_low_rel"] = 100 * np.maximum(df["close"] / df[f"year_low"] - 1, 0)
    df[f"year_high_rel"] = 100 * np.maximum(1 - df["close"] / df[f"year_high"], 0)
    return df


def append_oscillators(df):
    for osc in get_oscs():
        temp = osc_function(df, osc)
        if isinstance(temp, pd.DataFrame) and len(temp.columns) > 1:
            df[[osc + suffix for suffix in SUFFIXES[osc]]] = temp
        else:
            df[osc] = temp

    return df


def group_price_data(df):
    df = df.groupby(
        [
            df.index.isocalendar().year,
            df.index.isocalendar().week,
        ]
    ).last()

    df["date"] = pd.to_datetime(df["date"]).apply(
        lambda d: d + datetime.timedelta(days=4 - d.weekday())
        if d + datetime.timedelta(days=7) < datetime.datetime.now().date()
        else d
    )
    df.index = df["date"]
    df["growth"] = df["close"].pct_change().shift(-1) + 1
    df["growth"] = df["growth"].where(df["growth"] < 5)

    return df


def convert_financial_data(df, local_currency="USD", ignore_cols=[]):
    if not (df["reportedCurrency"] == local_currency).all():
        df["currency_idx"] = list(
            df.apply(
                lambda row: (CURRENCY_DATE_SERIES - row.name).abs().idxmin(), axis=1
            )
        )
        df["currency_rate"] = df.apply(
            lambda row: CURRENCY_RATES.loc[row["currency_idx"], local_currency] / CURRENCY_RATES.loc[row["currency_idx"], row["reportedCurrency"]],
            axis=1,
        )
        drop_cols = ["reportedCurrency", "currency_idx", "currency_rate"]
        mult_cols = [c for c in df if c not in drop_cols and c not in ignore_cols]

        df.loc[:, mult_cols] = df.loc[:, mult_cols].multiply(
            df["currency_rate"], axis=0
        )
        df.drop(columns=drop_cols, inplace=True)
    else:
        df.drop(columns=["reportedCurrency"], inplace=True)

    return df


FINANCIALS_DROP = [
    "symbol",
    "calendarYear",
    "period",
    # "reportedCurrency",
    "cik",
    "fillingDate",
    "acceptedDate",
    "link",
    "finalLink",
]


def get_financial_data(
    ticker, balance_json, income_json, cashflow_json, earnings_dates_json, local_currency="USD"
):
    balance = pd.DataFrame(balance_json)
    balance.index = pd.to_datetime(balance["date"])
    balance.drop(
        columns=FINANCIALS_DROP + ["preferredStock", "commonStock", "date"],
        inplace=True,
    )
    balance = convert_financial_data(balance, local_currency=local_currency)

    income = pd.DataFrame(income_json)
    income.index = pd.to_datetime(income["date"])
    ratio_cols = [c for c in income.columns if c.lower().endswith("ratio")]
    income.drop(
        columns=FINANCIALS_DROP + ratio_cols + ["weightedAverageShsOut", "eps"],
        inplace=True,
    )
    income = convert_financial_data(income, local_currency=local_currency, ignore_cols=["date", "weightedAverageShsOutDil"])

    cashflow = pd.DataFrame(cashflow_json)
    if len(cashflow) == 0:
        cashflow = pd.DataFrame()
    else:
        cashflow.index = pd.to_datetime(cashflow["date"])
        already_included_cols = [
            "depreciationAndAmortization",
            "netIncome",
            "inventory",
            "date",
        ]
        cashflow.drop(columns=FINANCIALS_DROP + already_included_cols, inplace=True)
    cashflow = convert_financial_data(cashflow, local_currency=local_currency)

    no_dates = earnings_dates_json is None or len(earnings_dates_json) == 0
    if no_dates:
        earnings_dates = pd.DataFrame()
    else:
        earnings_dates = pd.DataFrame(earnings_dates_json)
        earnings_dates.drop_duplicates(
            subset="fiscalDateEnding", keep="last", inplace=True
        )  # Drop annual reports when they have same end as quarter
        earnings_dates.index = pd.to_datetime(earnings_dates["fiscalDateEnding"])
        earnings_dates = earnings_dates[["date"]]
        earnings_dates.rename(columns={"date": "reporting_date"}, inplace=True)

    financials = pd.concat([balance, income, cashflow], axis=1)
    financials = pd.merge(
        financials, earnings_dates, how="left", left_index=True, right_index=True
    ).sort_index()
    if not no_dates:
        financials.index = pd.to_datetime(
            financials["reporting_date"].fillna(financials["date"])
        )
    if len(cashflow) == 0:
        financials[
            [
                "operatingCashFlow",
                "accountsReceivables",
                "netCashProvidedByOperatingActivities",
            ]
        ] = np.nan
    financials.drop(columns=["date"], inplace=True)

    annual_sum_cols = [
        c for c in income.columns if c not in ["weightedAverageShsOutDil", "date"]
    ] + list(cashflow.columns)
    financials[annual_sum_cols] = financials[annual_sum_cols].rolling(4).sum()

    annual_avg_cols = [
        "shortTermDebt",
        "longTermDebt",
        "cashAndShortTermInvestments",
        "totalAssets",
        "totalCurrentAssets",
        "totalCurrentLiabilities",
        "totalEquity",
    ]
    financials[[c + "_annual_avg" for c in annual_avg_cols]] = (
        financials[annual_avg_cols].rolling(4).mean()
    )

    financials["ebit"] = (
        financials["ebitda"] - financials["depreciationAndAmortization"]
    )
    financials["eps_growth"] = (
        100 * financials["epsdiluted"] / financials["epsdiluted"].shift(4) - 100
    )
    financials["book_value"] = (
        financials["totalAssets"] - financials["totalLiabilities"]
    )
    financials["current_ratio"] = (
        financials["totalCurrentAssets"] / financials["totalCurrentLiabilities"]
    )

    financials["roe"] = (
        100
        * financials["netIncome"]
        / financials["totalEquity_annual_avg"].replace(0, np.nan)
    )
    financials["roa"] = (
        100
        * financials["netIncome"]
        / financials["totalAssets_annual_avg"].replace(0, np.nan)
    )
    financials["roce"] = (
        100
        * financials["ebit"]
        / (
            financials["totalAssets_annual_avg"]
            - financials["totalCurrentLiabilities_annual_avg"]
        ).replace(0, np.nan)
    )
    financials["roic"] = (
        100
        * (
            financials["operatingIncome"]
            + financials["totalOtherIncomeExpensesNet"]
            - financials["incomeTaxExpense"]
        )
        / (
            financials["shortTermDebt_annual_avg"]
            + financials["longTermDebt_annual_avg"]
            + financials["totalEquity_annual_avg"]
        ).replace(0, np.nan)
    )
    financials["rod"] = (
        100
        * financials["netIncome"]
        / (
            financials["longTermDebt_annual_avg"]
            + financials["shortTermDebt_annual_avg"]
        ).replace(0, np.nan)
    )
    financials["current_ratio"] = (
        financials["totalCurrentAssets"] / financials["totalCurrentLiabilities"]
    )
    financials["quick_ratio"] = (
        financials["cashAndShortTermInvestments"]
        + financials["accountsReceivables"].fillna(0)
    ) / financials["totalCurrentLiabilities"]
    financials["cash_ratio"] = (
        financials["cashAndShortTermInvestments"]
        / financials["totalCurrentLiabilities"]
    )
    financials["ocf_ratio"] = (
        financials["netCashProvidedByOperatingActivities"]
        / financials["totalCurrentLiabilities"]
    )
    financials["wct"] = financials["revenue"] / (
        financials["totalCurrentAssets_annual_avg"]
        - financials["totalCurrentLiabilities_annual_avg"]
    ).replace(0, np.nan)
    financials["de"] = (
        financials["shortTermDebt"] + financials["longTermDebt"]
    ) / financials["totalEquity"]
    financials["da"] = (
        financials["shortTermDebt"] + financials["longTermDebt"]
    ) / financials["totalAssets"]
    financials["ea"] = financials["totalEquity"] / financials["totalAssets"]

    financials["gross_margin"] = financials["grossProfit"] / financials["revenue"]
    financials["asset_turnover_ratio"] = (
        financials["revenue"] / financials["totalAssets_annual_avg"]
    )
    financials["piotroski"] = (
        (financials["netIncome"] > 0).astype(int)
        + (financials["roa"] > 0).astype(int)
        + (financials["operatingCashFlow"] > 0).astype(int)
        + (
            financials["netCashProvidedByOperatingActivities"] > financials["netIncome"]
        ).astype(int)
        + (financials["longTermDebt"] < financials["longTermDebt"].shift(4)).astype(int)
        + (financials["current_ratio"] > financials["current_ratio"].shift(4)).astype(
            int
        )
        + (
            financials["weightedAverageShsOutDil"]
            <= financials["weightedAverageShsOutDil"].shift(4)
        ).astype(int)
        + (financials["gross_margin"] > financials["gross_margin"].shift(4)).astype(int)
        + (
            financials["asset_turnover_ratio"]
            > financials["asset_turnover_ratio"].shift(4)
        ).astype(int)
    )

    cagr_cols = ["revenue", "ebitda", "ebit", "netIncome"]
    zero_division_cols = ["totalCurrentLiabilities", "totalEquity", "totalAssets"]
    margin_cols = ["ebitda", "ebit", "netIncome"]

    financials.loc[:, cagr_cols + zero_division_cols].replace(0, np.nan, inplace=True)

    financials[[c.replace("netIncome", "profit") + "_5y_cagr" for c in cagr_cols]] = (
        100 * (financials[cagr_cols] / financials[cagr_cols].shift(5 * 4)) ** (1 / 5)
        - 100
    )

    financials[
        [c.replace("netIncome", "profit") + "_margin" for c in margin_cols]
    ] = 100 * financials[margin_cols].divide(financials["revenue"], axis=0)

    return financials


def get_dividend_data(dividend_json):
    if "historical" not in dividend_json:
        return None
    dividend = pd.DataFrame(dividend_json["historical"]).iloc[::-1]
    dividend.index = pd.to_datetime(dividend["date"])
    dividend = dividend[["adjDividend", "dividend"]]
    return dividend


def merge_in_financial_data(df, financials, dividend, profile_json, local_currency="USD"):
    df = pd.merge(df, financials, how="outer", left_index=True, right_index=True)
    df[financials.columns] = df.loc[:, financials.columns].fillna(method="ffill")

    if dividend is None:
        df[["dividend", "adjDividend"]] = 0
    else:
        df = pd.merge(df, dividend, how="outer", left_index=True, right_index=True)
        df[["dividend", "adjDividend"]] = (
            df[["dividend", "adjDividend"]].rolling("364d").sum().fillna(0)
        )

    df["market_cap"] = df["close"] * df["weightedAverageShsOutDil"] if profile_json[0]["mktCap"] != 0 else np.nan
    
    df["usd_rate"] = CURRENCY_RATES[local_currency]
    df["usd_rate"] = df["usd_rate"].fillna(method="ffill").fillna(method="bfill")
    df["market_cap_usd"] = df["market_cap"] / df["usd_rate"]

    df["ev"] = (
        df["market_cap"]
        + df["shortTermDebt_annual_avg"]
        + df["longTermDebt_annual_avg"]
        + df["cashAndShortTermInvestments_annual_avg"]
    )
    df["dividend_yield_percent"] = 100 * df["adjDividend"] / df["close"]
    df["pb"] = df["market_cap"] / df["book_value"].replace(0, np.nan)
    df["ps"] = df["market_cap"] / df["revenue"].replace(0, np.nan)
    df["pe"] = df["market_cap"] / df["netIncome"].replace(0, np.nan)
    df["pcf"] = df["market_cap"] / df["netCashProvidedByOperatingActivities"].replace(
        0, np.nan
    )
    df["evs"] = df["ev"] / df["revenue"]
    df["evebitda"] = df["ev"] / df["ebitda"]
    df["evebit"] = df["ev"] / df["ebit"]
    df["evnopat"] = df["ev"] / (df["operatingIncome"] - df["incomeTaxExpense"]).replace(
        0, np.nan
    )

    df["peg"] = df["pe"] / df["eps_growth"].replace(0, np.nan)
    df.loc[(df["pe"] < 0) | (df["eps_growth"] < 0), "peg"] = np.nan

    df["turnover_percent"] = 100 * df["volume"] / df["weightedAverageShsOutDil"]

    df["altman_z"] = (
        1.2
        * (df["totalCurrentAssets"] - df["totalCurrentLiabilities"])
        / df["totalAssets"]
        + 1.4 * df["retainedEarnings"] / df["totalAssets"]
        + 3.3 * df["ebit"] / df["totalLiabilities"]
        + 0.6 * df["market_cap"] / df["totalLiabilities"]
        + 1.0 * df["revenue"] / df["totalAssets"]
    )

    return df


def append_ownership(df, ticker, ownership_json):
    ownership_cols = [
        "ownershipPercent",
        "ownershipPercentChange",
        "putCallRatio",
        "putCallRatioChange",
    ]
    if ownership_json is None or len(ownership_json) == 0:
        df[ownership_cols] = np.nan
    else:
        ownership = pd.DataFrame(ownership_json)
        ownership.index = pd.to_datetime(ownership["date"])
        ownership = ownership[ownership_cols]
        df = pd.merge(df, ownership, how="outer", left_index=True, right_index=True)
        df.loc[:, list(ownership.columns)] = df[list(ownership.columns)].fillna(
            method="ffill"
        )

    return df


def append_grades(df, ticker, grades_json):
    if grades_json is None or len(grades_json) == 0:
        df["grade"] = np.nan
    else:
        grades = pd.DataFrame(grades_json)
        grades["newGrade"] = (
            grades["newGrade"]
            .str.lower()
            .replace(
                {
                    "strong sell": 3,
                    "sell": -2,
                    "underweight": -1,
                    "reduce": -1,
                    "underperformer": -1,
                    "market underperform": -1,
                    "sector underperform": -1,
                    "underperform": -1,
                    "negative": -1,
                    "market perform": 0,
                    "sector perform": 0,
                    "peer perform": 0,
                    "perform": 0,
                    "neutral": 0,
                    "hold": 0,
                    "equal-weight": 0,
                    "sector weight": 0,
                    "in-line": 0,
                    "overweight": 1,
                    "accumulate": 1,
                    "market outperform": 1,
                    "sector outperform": 1,
                    "outperform": 1,
                    "positive": 1,
                    "buy": 2,
                    "long-term buy": 2,
                    "strong buy": 3,
                }
            )
        )

        grades = grades[grades["newGrade"].apply(lambda g: isinstance(g, int))].iloc[
            ::-1
        ]
        grades = grades.pivot(index="date", columns="gradingCompany", values="newGrade")
        grades.index = pd.to_datetime(grades.index)

        grade_consensus = (
            grades.resample("1d").first().fillna(method="ffill", limit=365).mean(axis=1)
        )
        grade_consensus.name = "grade"

        df = pd.merge(
            df, grade_consensus, how="left", left_index=True, right_index=True
        )
        df["grade"].fillna(method="ffill", inplace=True)

    return df


def append_profile_data(df, ticker, profile_json):
    profile = profile_json[0]

    if "." in ticker:
        df["country"] = COUNTRY_CODES[ticker[ticker.index(".") + 1 :]]
    else:
        df["country"] = "US"
    df["ticker"] = profile["symbol"]
    df["name"] = profile["companyName"]
    df["industry"] = profile["industry"]
    df["sector"] = profile["sector"]

    return df


def select_and_rename(df, years):
    df = df.loc[df.index[-1] - df.index <= datetime.timedelta(days=365 * years)].dropna(
        subset=["close"]
    )

    df.rename(
        columns={
            "dividend": "dps",
            "epsdiluted": "eps",
            "ownershipPercent": "ownership_percent",
            "ownershipPercentChange": "ownership_percent_change",
            "putCallRatio": "put_call_ratio",
            "putCallRatioChange": "put_call_ratio_change",
        },
        inplace=True,
    )

    int_cols = [c for c in df if c.startswith("days_since_")] + ["piotroski"]
    df.loc[:, int_cols] = df[int_cols].fillna(-101).astype("int16").replace(-101, None)

    df = df.astype(object).replace({np.nan: None, np.inf: None, -np.inf: None})

    return df[HISTORICAL_COLUMNS]


from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


async def get_historical_data(ticker, years=1, buffer_years=1.5, responses=None):
    # sys.stdout = open(os.devnull, "w")  # Blocks prints

    is_usa = "." not in ticker
    local_currency = CURRENCIES["US" if is_usa else ticker[ticker.index(".") + 1 :]]

    if responses is None:
        urls = get_urls(ticker, years, buffer_years, is_usa)
        responses = await send_requests_parallell(urls)
    if not is_usa:
        responses["earnings_dates"] = None
        responses["ownership"] = None
        responses["grades"] = None

    df = get_price_data(responses["prices"], responses["quote"])
    df = append_oscillators(df)
    df = append_extrema(df)
    df = append_patterns(df)

    df = group_price_data(df)

    financials = get_financial_data(
        ticker,
        responses["balance"],
        responses["income"],
        responses["cashflow"],
        responses["earnings_dates"],
        local_currency=local_currency
    )
    dividend = get_dividend_data(responses["dividend"])
    df = merge_in_financial_data(df, financials, dividend, responses["profile"], local_currency=local_currency)

    df = append_ownership(df, ticker, responses["ownership"])
    df = append_grades(df, ticker, responses["grades"])
    df = append_profile_data(df, ticker, responses["profile"])

    df = select_and_rename(df, years)
    return df
