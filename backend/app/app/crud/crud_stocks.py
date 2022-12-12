from datetime import datetime, timedelta
import logging
from typing import Optional

from fastapi import HTTPException, status
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.dialects import postgresql

from app.crud.crud_utils import utils
from app.models import Historical, ScreeningTicker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDStock:
    def get_historical_performance(
        self, criteria: str, start_time: datetime, end_time: datetime, db: Session
    ):

        (
            range_criteria_list,
            value_criteria_list,
            bool_criteria_list,
        ) = utils.get_criteria_lists(criteria)

        query_ands = utils.get_criteria_ands(
            range_criteria_list, value_criteria_list, bool_criteria_list
        )

        
        query_ands.append(Historical.market_cap_usd > 1e8)
        if end_time:
            query_ands.append(Historical.date < end_time)
        if (datetime.now() - start_time).days < 365 * 10:
            query_ands.append(Historical.date > start_time)

        res = (
            db.query(Historical.date, func.avg(Historical.growth).label("growth"))
            .filter(*query_ands)
            .group_by(Historical.date)
            .order_by(Historical.date)
            .all()
        )

        return res

    def get_historical_data(
        self,
        ticker: str,
        columns: str,
        start_date: datetime,
        end_time: datetime,
        db: Session,
    ):

        columns_list = columns.split(",")
        for col in columns_list:
            if col not in Historical.__dict__.keys():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Column '{col}' is not in historical",
                )

        if end_time:
            result = (
                db.query(*[Historical.__dict__[col] for col in columns_list])
                .filter(
                    Historical.ticker == ticker,
                    Historical.date > start_date,
                    Historical.date < end_time,
                )
                .order_by(Historical.date)
                .all()
            )
        else:
            result = (
                db.query(*[Historical.__dict__[col] for col in columns_list])
                .filter(
                    Historical.ticker == ticker,
                    Historical.date > start_date,
                )
                .order_by(Historical.date)
                .all()
            )

        result_count = len(result)
        if result_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No ticker in historical database with name '{ticker}' in this time period",
            )

        max_count = 300
        if result_count <= max_count:
            return result

        # Return evenly spaced values if result_count > max_count
        idx = np.round(np.linspace(0, result_count - 1, max_count)).astype(int)
        return [result[i] for i in idx]

    def get_current_data(self, ticker: str, columns: str, db: Session):
        columns_list = columns.split(",")
        for col in columns_list:
            if col not in ScreeningTicker.__dict__.keys():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Column '{col}' is not in screening_ticker",
                )

        try:
            result = (
                db.query(*[ScreeningTicker.__dict__[col] for col in columns_list])
                .filter(ScreeningTicker.ticker == ticker)
                .first()
            )
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No ticker in screening_ticker database with name '{ticker}'",
            )

        return result

    def get_tickers_with_criteria(
        self,
        criteria: str,
        page: int,
        size: int,
        sort_column: Optional[str],
        sort_order: Optional[str],
        db: Session,
    ):

        (
            range_criteria_list,
            value_criteria_list,
            bool_criteria_list,
        ) = utils.get_criteria_lists(criteria)

        query_ands = utils.get_criteria_ands(
            range_criteria_list,
            value_criteria_list,
            bool_criteria_list,
            table=ScreeningTicker,
        )
        # maxdate_query = utils.get_max_date_query(db)

        print(range_criteria_list)

        to_query = [
            ScreeningTicker.ticker,
            ScreeningTicker.name,
            *[
                ScreeningTicker.__dict__[range_crit[0]]
                for range_crit in range_criteria_list
            ],
            *[
                ScreeningTicker.__dict__[value_crit[0]]
                for value_crit in value_criteria_list
                if value_crit[0] != "country"
            ],
            *[
                ScreeningTicker.__dict__[bool_crit[0]]
                for bool_crit in bool_criteria_list
            ],
        ]

        if sort_column != "market_cap" and ScreeningTicker.market_cap not in to_query:
            to_query.append(ScreeningTicker.market_cap)

        if sort_column and ScreeningTicker.__dict__[sort_column] not in to_query:
            to_query.append(ScreeningTicker.__dict__[sort_column])

        if len(to_query) <= 4 and ScreeningTicker.close not in to_query:
            to_query.append(ScreeningTicker.close)

        if (len(to_query) <= 4) and ScreeningTicker.pe not in to_query:
            to_query.append(ScreeningTicker.pe)

        if len(to_query) <= 4 and ScreeningTicker.pb not in to_query:
            to_query.append(ScreeningTicker.pb)

        query = db.query(*to_query).filter(
            *query_ands,
            ScreeningTicker.date >= datetime.now().date() - timedelta(days=14),
        )

        if sort_column is not None:
            if sort_order == "desc":
                query = query.order_by(ScreeningTicker.__dict__[sort_column].desc())
            elif sort_order == "asc":
                query = query.order_by(ScreeningTicker.__dict__[sort_column].asc())

        result = query.offset(page * size).limit(size).all()

        if len(result) < size:
            count = len(result) + size * page
        else:
            count = (
                db.query(func.count())
                .filter(
                    *query_ands,
                    ScreeningTicker.date >= datetime.now().date() - timedelta(days=14),
                )
                .one()
            )[0]

        return result, count


stocks = CRUDStock()
