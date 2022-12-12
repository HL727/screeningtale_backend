from datetime import date, datetime
from typing import List, Optional
from celery.utils.log import get_task_logger
import pandas as pd
import numpy as np
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from asgiref.sync import async_to_sync

from app.worker import app
from app.utils import make_dataset
from app.utils.tickers import batch_tickers
from app import models
from app.db.session import session_scope

logger = get_task_logger(__name__)


def convert_bool(vals: dict) -> None:
    for key, val in vals.items():
        if type(val) == bool:
            if val == False:
                vals[key] = 0
            elif val == True:
                vals[key] = 1


@app.task(acks_late=True)
def insert_historical(ticker: str, last_date=None, years=1, buffer_years=1.5) -> dict:
    result = async_to_sync(insert_historical_async)(
        ticker, last_date, years, buffer_years
    )
    return result


async def insert_historical_async(
    ticker: str, last_date=None, years=1, buffer_years=1.5
) -> dict:
    logger.info("Starting insert_historical task")
    datapoints = None
    try:
        df: pd.DataFrame = await make_dataset.get_historical_data(
            ticker, years=years, buffer_years=buffer_years
        )
        if last_date:
            df = df[df.index > last_date]
        if len(df) == 0:
            logger.info(f"No new data available for {ticker}")
            status = "unchanged"
        else:
            data = df.to_dict(orient="records")
            datapoints = len(data)
            with session_scope() as db:
                (
                    db.query(models.Historical)
                    .filter(
                        models.Historical.ticker == ticker,
                        models.Historical.growth == None,
                    )
                    .delete()
                )
                (
                    db.query(models.ScreeningTicker)
                    .filter(
                        models.ScreeningTicker.ticker == ticker,
                    )
                    .delete()
                )
                db.add(models.ScreeningTicker(**data[-1]))
                db.bulk_insert_mappings(models.Historical, data)
                # df.iloc[-1, :].to_sql(
                #     name="screening_ticker", con=db, if_exists="append", index=False
                # )
                # df.to_sql(
                #     name="historical",
                #     con=db,
                #     if_exists="append",
                #     index=False,
                #     method="multi",
                # )

            status = "success"
    except Exception as err:
        logger.info(f"Error occured {err}")
        status = "error"

    return {"ticker": ticker, "status": status, "datapoints": datapoints}


@app.task(acks_late=True)
def insert_all_historicals(countries: List[str], priority=None) -> dict:
    logger.info(f"Start to insert_all_historicals")

    with session_scope() as db:
        # stocks_and_dates = (
        #     db.query(models.ScreeningTicker)
        #     .with_entities(models.ScreeningTicker.ticker, models.ScreeningTicker.date)
        #     .all()
        # )
        stocks_and_dates = (
            db.query(models.Historical)
            .filter(models.Historical.growth != np.nan)
            .with_entities(models.Historical.ticker, func.max(models.Historical.date))
            .group_by(models.Historical.ticker)
            .all()
        )

    today = datetime.now().date()

    if countries:
        stocks_and_dates = [
            sd
            for sd in stocks_and_dates
            if (
                ("." not in sd[0] and "US" in countries)
                or ("." in sd[0] and sd[0][sd[0].index(".") + 1 :] in countries)
            )
            and ((today - sd[1]).days < 30)
        ]

    tickers = [el[0] for el in stocks_and_dates]
    dates = [el[1] for el in stocks_and_dates]
    for i in range(len(tickers)):
        insert_historical.apply_async((tickers[i], dates[i]), priority=priority)
    return {"tickers": len(stocks_and_dates)}


@app.task(acks_late=True)
def cluster_historical() -> dict:
    try:
        with session_scope() as db:
            (
                db.execute(
                    """
                    CLUSTER historical; ANALYZE historical
                """
                )
            )
        return {"status": "success"}
    except:
        return {"status": "error"}


# -------------------------------------------------------------------------------------
# The code below was an attempt to handle several tickers in batch, to parallellize API calls. Even a batch size as small as 2 gave aiohttp.client_exceptions.ContentTypeError.
# Leaving code in case we want to reattempt this approach at a later time.

# @app.task(acks_late=True)
# def insert_historical_batch(tickers: List[str]) -> dict:
#     result = async_to_sync(insert_historical_batch_async)(tickers)
#     return result


# async def get_batch_responses(tickers: List[str], years, buffer_years):
#     url_dicts = [
#         make_dataset.get_urls(ticker, years, buffer_years, "." not in ticker)
#         for ticker in tickers
#     ]
#     main_url_dict = {
#         f"{list(url_dicts[i].keys())[j]}_{tickers[i]}": list(url_dicts[i].values())[j]
#         for i in range(len(tickers))
#         for j in range(len(url_dicts[i]))
#     }
#     responses = await make_dataset.send_requests_parallell(main_url_dict)
#     responses_dict = {
#         ticker: {
#             key.replace(f"_{ticker}", ""): value
#             for key, value in responses.items()
#             if key.endswith(f"_{ticker}")
#         }
#         for ticker in tickers
#     }
#     return responses_dict


# async def insert_historical_batch_async(
#     tickers: List[str],
#     last_dates: List[date] = [],
#     years=1,
#     buffer_years=1.5,
#     last_date=None,
# ) -> dict:
#     logger.info("Starting insert_historical task")

#     responses_dict = await get_batch_responses(
#         tickers, years=years, buffer_years=buffer_years
#     )
#     messages = {}
#     for i in range(len(tickers)):
#         ticker = tickers[i]
#         if last_dates:
#             last_date = last_dates[i]
#         datapoints = None
#         try:
#             df: pd.DataFrame = await make_dataset.get_historical_data(
#                 ticker,
#                 years=years,
#                 buffer_years=buffer_years,
#                 responses=responses_dict[ticker],
#             )
#             if last_dates:
#                 df = df[df.index > last_date]
#             if len(df) == 0:
#                 logger.info(f"No new data available for {ticker}")
#                 status = "unchanged"
#             else:
#                 data = df.to_dict(orient="records")
#                 datapoints = len(data)
#                 new_last_date = df.index.max()
#                 if last_date:
#                     keep_last_date = (new_last_date.weekday() < last_date.weekday()) | (
#                         (new_last_date - last_date).days >= 7
#                     )
#                 else:
#                     keep_last_date = True
#                 with session_scope() as db:
#                     (
#                         db.query(models.ScreeningTicker)
#                         .filter(models.ScreeningTicker.ticker == ticker)
#                         .delete()
#                     )
#                     db.add(models.ScreeningTicker(**data[-1]))
#                     if not keep_last_date:
#                         (
#                             db.query(models.Historical)
#                             .filter(
#                                 models.Historical.ticker == ticker,
#                                 models.Historical.date == last_date,
#                             )
#                             .delete()
#                         )
#                     db.bulk_insert_mappings(models.Historical, data)

#                 status = "success"
#         except Exception as err:
#             logger.info(f"Error occured {err}")
#             status = "error"
#         messages[ticker] = {"status": status, "datapoints": datapoints}

#     return messages

# @app.task(acks_late=True)
# def insert_all_historicals() -> dict:
#     logger.info(f"Start to insert_all_historicals")

#     with session_scope() as db:
#         stocks_and_dates = (
#             db.query(models.ScreeningTicker)
#             .with_entities(models.ScreeningTicker.ticker, models.ScreeningTicker.date)
#             .all()
#         )
#     logger.info(stocks_and_dates)

#     ticker_batches = batch_tickers(
#         [el[0] for el in stocks_and_dates], batch_size=BATCH_SIZE
#     )
#     date_batches = batch_tickers(
#         [el[1] for el in stocks_and_dates], batch_size=BATCH_SIZE
#     )
#     logger.info(ticker_batches)
#     for i in range(len(ticker_batches)):
#         insert_historical_batch.apply_async((ticker_batches[i], date_batches[i]))
#     return {"tickers": len(stocks_and_dates)}
