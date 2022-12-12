import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import pandas as pd

from app import crud, schemas
from app.api.dependencies import get_db
from app.utils.api_route_classes.ratelimit import RateLimitAPIRoute


router = APIRouter(route_class=RateLimitAPIRoute)


@router.get(
    "/historical_performance",
    response_model=schemas.stocks.HistoricalPerformance,
)
def historical_performance_view(
    q: str,
    start_time: str,
    end_time: Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        start_datetime: datetime.datetime = datetime.datetime.strptime(
            start_time, "%d-%m-%Y"
        )
        if end_time:
            end_datetime: datetime.datetime = datetime.datetime.strptime(
                end_time, "%d-%m-%Y"
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date input on wrong format, should be dd-mm-yyyy",
        )
    if end_time:
        if start_datetime > end_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time",
            )

        res = crud.stocks.get_historical_performance(
            q, start_datetime, end_datetime, db
        )

    else:
        res = crud.stocks.get_historical_performance(q, start_datetime, None, db)

    historical_date_list: List[schemas.stocks.HistoricalDate] = []

    cumulative_growth_list = []
    cumulative_growth = 1.0
    for result in res:
        day = schemas.stocks.HistoricalDate.from_orm(result)
        if not pd.isnull(day.growth):
            historical_date_list.append(day)

            next_growth = 100 * cumulative_growth
            cumulative_growth_list.append(next_growth)
            cumulative_growth *= (
                day.growth - 0.0005
            )  # Subtracting 0.05% in kurtasje and spread from each transaction

    historical_date_list_return: List[schemas.stocks.HistoricalDateReturn] = []
    for i in range(len(historical_date_list)):
        to_append = schemas.stocks.HistoricalDateReturn.parse_obj(
            {"date": historical_date_list[i].date, "close": cumulative_growth_list[i]}
        )
        historical_date_list_return.append(to_append)

    if len(res) > 0:
        if end_time:
            max_date = end_datetime
        else:
            max_date = datetime.datetime.now()
        time_difference = (
            max_date.year
            - historical_date_list[0].date.year
            + 1 / 12 * (max_date.month - historical_date_list[0].date.month)
            + 1 / 365.25 * (max_date.day - historical_date_list[0].date.day)
        )
    else:
        time_difference = 1

    if cumulative_growth < 0:
        CAGR = -100
    elif len(res) > 0:
        CAGR = 100 * (cumulative_growth ** (1 / time_difference) - 1)
    else:
        CAGR = 0

    out = schemas.stocks.HistoricalPerformance.parse_obj(
        {"CAGR": CAGR, "historical": historical_date_list_return}
    )
    # return {"CAGR": 4, "historical": [], "max_date": max_date_res}
    return out


@router.get(
    "/historical_data/{ticker}",
    response_model=List[schemas.stocks.Historical],
    response_model_exclude_none=True,
)
def historical_data_view(
    ticker: str,
    columns: str,
    start_time: str,
    end_time: Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        start_datetime: datetime.datetime = datetime.datetime.strptime(
            start_time, "%d-%m-%Y"
        )
        if end_time:
            end_datetime: datetime.datetime = datetime.datetime.strptime(
                end_time, "%d-%m-%Y"
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date input on wrong format, should be dd-mm-yyyy",
        )

    if end_time:
        result = crud.stocks.get_historical_data(
            ticker, columns, start_datetime, end_datetime, db
        )
    else:
        result = crud.stocks.get_historical_data(
            ticker, columns, start_datetime, None, db
        )
    # out: List[schemas.stocks.Historical] = []
    # for res_row in result:
    #     day = schemas.stocks.Historical.from_orm(res_row)
    #     out.append(day)

    return result


@router.get(
    "/current_data/{ticker}",
    response_model=schemas.stocks.Historical,
    response_model_exclude_none=True,
)
def current_data_view(ticker: str, columns: str, db: Session = Depends(get_db)):
    result = crud.stocks.get_current_data(ticker, columns, db)
    out = schemas.stocks.Historical.from_orm(result)
    return out


@router.get(
    "/tickers_with_criteria",
    response_model=schemas.stocks.TickersWithCriteria,
    response_model_exclude_none=True,
)
def tickers_with_criteria_view(
    q: str,
    page: int,
    size: int,
    sort_column: Optional[str] = "market_cap",
    sort_order: Optional[str] = "desc",
    db: Session = Depends(get_db),
):
    result, count = crud.stocks.get_tickers_with_criteria(
        q, page, size, sort_column, sort_order, db
    )
    # out: List[schemas.stocks.Historical] = []
    # for row in result:
    #     ticker = schemas.stocks.Historical.from_orm(row)
    #     out.append(ticker)

    print(result)

    return {"results": result, "count": count}
