import datetime
import re
from typing import Any, List

import numpy as np
import pandas as pd
from fastapi import HTTPException, status
from pandas.core.series import Series
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models import (
    Historical,
    Screener,
)


class CRUDUtils:

    def get_screener_count(self, user_id: int, db: Session):
        return db.query(func.count(1)).filter(Screener.creator_id == user_id).one()[0]

    def validate_criteria_string(self, criteria: str):
        criteria_list = criteria.split(",")
        regex_list = [
            "^value:[A-Za-z| ]+;[A-Za-z|\\-— ]+$",
            "^range:[A-Za-z0-9_\\-— ]+;-?(\d+(?:\.\d+)?)?;-?(\d+(?:\.\d+)?)?$",
            "^bool:[A-Za-z]+;(True|False)$",
            "^value:[A-Za-z| ]+;[A-Za-z|\\-— ]+;(True|False)$",
        ]
        for criteria_element in criteria_list:
            if not (
                bool(re.match(regex_list[0], criteria_element))
                or bool(re.match(regex_list[1], criteria_element))
                or bool(re.match(regex_list[2], criteria_element))
                or bool(re.match(regex_list[3], criteria_element))
                or criteria_element == ""
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Criteria string '{criteria_element}' is on wrong format",
                )

    def get_criteria_lists(self, criteria: str):
        criteria_list = criteria.split(",")
        self.validate_criteria_string(criteria)

        range_criteria_list = []
        value_criteria_list = []
        bool_criteria_list = []

        if len(criteria) > 0:
            if "value:country" not in criteria:
                value_criteria_list.append(["country", ["US"]])
            for criteria in criteria_list:
                crit_type, values = criteria.split(":")
                if crit_type == "value":
                    to_append = values.split(";")
                    to_append[1] = to_append[1].split("|")
                    value_criteria_list.append(to_append)
                elif crit_type == "range":
                    to_append = values.split(";")
                    if to_append[1] != "":
                        to_append[1] = float(to_append[1])
                    if to_append[2] != "":
                        to_append[2] = float(to_append[2])
                    range_criteria_list.append(to_append)
                elif crit_type == "bool":
                    to_append = values.split(";")
                    if to_append[1] == "True":
                        to_append[1] = 1
                    else:
                        to_append[1] = 0
                    bool_criteria_list.append(to_append)

        for criteria_element in (
            range_criteria_list + value_criteria_list + bool_criteria_list
        ):
            col = criteria_element[0]
            if not Historical.__dict__.keys().__contains__(col):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Column '{col}' is not in historical",
                )

        return range_criteria_list, value_criteria_list, bool_criteria_list

    def get_criteria_ands(
        self,
        range_criteria_list: List[Any],
        value_criteria_list: List[Any],
        bool_criteria_list: List[Any],
        table=Historical,
    ):

        ands = []

        for range_crit in range_criteria_list:
            if range_crit[1] != "":
                ands.append(table.__dict__[range_crit[0]] > range_crit[1])
            if range_crit[2] != "":
                ands.append(table.__dict__[range_crit[0]] < range_crit[2])

        for value_crit in value_criteria_list:
            ands.append(
                or_(*[table.__dict__[value_crit[0]] == val for val in value_crit[1]])
            )

        for bool_crit in bool_criteria_list:
            ands.append(table.__dict__[bool_crit[0]] == bool_crit[1])

        return ands

    def get_max_date_query(self, db: Session):
        maxdate_query = (
            db.query(Historical.ticker, func.max(Historical.date).label("MaxDate"))
            .group_by(Historical.ticker)
            .subquery()
        )
        return maxdate_query

    def get_max_date_in_db(self, db: Session):
        max_date = db.query(func.max(Historical.date).label("MaxDate")).one()
        return max_date

    ## START USER UTILS

    def get_criteria_string(
        self,
        range_criteria_list: List[Any],
        value_criteria_list: List[Any],
        bool_criteria_list: List[Any],
    ):
        out_string = ""
        number_of_range_result = len(range_criteria_list)
        number_of_bool_result = len(bool_criteria_list)

        value_criteria_dict = {}
        for value_criteria in value_criteria_list:
            if value_criteria[0] in value_criteria_dict.keys():
                value_criteria_dict[value_criteria[0]].append(
                    [value_criteria[1], value_criteria[2]]
                )
            else:
                value_criteria_dict[value_criteria[0]] = [
                    [value_criteria[1], value_criteria[2]]
                ]

        value_criteria_keys = [key for key in value_criteria_dict.keys()]
        number_of_value_result = len(value_criteria_keys)
        for i in range(number_of_range_result):
            out_string += f"range:{range_criteria_list[i][0]};{range_criteria_list[i][1]};{range_criteria_list[i][2]}"
            if (
                i < number_of_range_result - 1
                or number_of_value_result > 0
                or number_of_bool_result > 0
            ):
                out_string += ","

        for i in range(number_of_value_result):
            out_string += f"value:{value_criteria_keys[i]};"
            for j in range(len(value_criteria_dict[value_criteria_keys[i]])):
                out_string += f"{value_criteria_dict[value_criteria_keys[i]][j][0]}"
                if j < len(value_criteria_dict[value_criteria_keys[i]]) - 1:
                    out_string += "|"
            if i < number_of_value_result - 1 or number_of_bool_result > 0:
                out_string += ","
        for i in range(number_of_bool_result):
            out_string += f"bool:{bool_criteria_list[i][0]};{bool_criteria_list[i][1]}"
            if i < number_of_bool_result - 1:
                out_string += ","

        return out_string

    def get_growth(self, candidate: Any, db: Session, annualized: bool = False):
        if isinstance(candidate, pd.DataFrame) or isinstance(candidate, Series):
            range_criteria_list, value_criteria_list, bool_criteria_list = candidate[
                ["range", "value", "bool"]
            ]
        else:
            (
                range_criteria_list,
                value_criteria_list,
                bool_criteria_list,
            ) = self.get_criteria_lists(candidate)
        query_ands = self.get_criteria_ands(
            range_criteria_list, value_criteria_list, bool_criteria_list
        )

        result = (
            db.query(func.avg(Historical.growth))
            .filter(*query_ands)
            .group_by(Historical.date)
            .all()
        )

        if len(result) > 0:
            growth = np.array(result)[:, 0].prod()
            if annualized:
                start_time = datetime.datetime(2003, 1, 1)
                end_time = datetime.datetime.today().date()
                time_difference = (
                    end_time.year
                    - start_time.year
                    + 1 / 12 * (end_time.month - start_time.month)
                    + 1 / 365.25 * (end_time.day - start_time.day)
                )
                return growth ** (1 / time_difference)
            else:
                return growth
        return (
            0  # Assuming we are not interested in screeners giving no historic matches
        )

    def get_string_representation_for_criteria(self, screener_id: int, db: Session):
        return db.query(Screener.criteria).filter(Screener.id == screener_id).one()

    def get_count(self, criteria: str, stock_db: Session, today: bool = True):

        maxdate_query = self.get_max_date_query(stock_db)

        (
            range_criteria_list,
            value_criteria_list,
            bool_criteria_list,
        ) = self.get_criteria_lists(criteria)
        query_ands = self.get_criteria_ands(
            range_criteria_list, value_criteria_list, bool_criteria_list
        )
        if today:
            count = (
                stock_db.query(Historical.ticker, Historical.date)
                .join(maxdate_query, Historical.ticker == maxdate_query.c.ticker)
                .filter(
                    *query_ands,
                    Historical.date == maxdate_query.c.MaxDate,
                )
                .count()
            )
        else:
            count = (
                stock_db.query(Historical.ticker, Historical.date)
                .filter(*query_ands)
                .count()
            )

        return count


utils = CRUDUtils()
