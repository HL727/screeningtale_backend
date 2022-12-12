import copy
import datetime

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api.dependencies import get_db

from app.utils.api_route_classes.ratelimit import RateLimitAPIRoute


router = APIRouter(route_class=RateLimitAPIRoute)

OPTIMIZE_PARAMS = {
    "limit": datetime.timedelta(seconds=10),  # Maximum time for optimizing
    # Number of surviving candidates per iteration
    "population": 2,
    # Relative maximum range value change per iteration
    "delta_per_iter": 0.3,
    # Chance of deleting instead of changing criteria on on iteration for one candidate
    "deletion_probability": 0.2,
}


@router.get("/optimize_screener", response_model=schemas.users.ScreenerOptimized)
def optimize_screener_view(q: str, db: Session = Depends(get_db)):
    start = datetime.datetime.now()
    start_growth = crud.utils.get_growth(q, db)
    (
        range_criteria_list,
        value_criteria_list,
        bool_criteria_list,
    ) = crud.utils.get_criteria_lists(q)
    candidates = pd.DataFrame(
        {
            0: {
                "range": range_criteria_list,
                "value": value_criteria_list,
                "bool": bool_criteria_list,
            }
        }
    ).T
    candidates["growth"] = crud.utils.get_growth(candidates.iloc[0], db)
    out_string = ""
    while datetime.datetime.now() - start < OPTIMIZE_PARAMS["limit"]:
        for cand_nr in range(len(candidates)):
            candidate = pd.Series(dtype=object)
            for c in candidates.columns:
                candidate[c] = copy.deepcopy(candidates[c].iloc[cand_nr])
            action = np.random.choice(
                ["change", "delete"],
                p=[
                    1 - OPTIMIZE_PARAMS["deletion_probability"],
                    OPTIMIZE_PARAMS["deletion_probability"],
                ],
            )
            if len(range_criteria_list) > 0 and action == "change":
                change_range_criterium(candidate["range"])
            elif (
                len(range_criteria_list) > 0
                and len(bool_criteria_list) > 0
                and len(value_criteria_list) > 0
            ):
                to_delete = np.random.choice(
                    [c for c in ["range", "value", "bool"] if len(candidate[c]) > 0]
                )
                remove_criterium(candidate[to_delete])
            elif len(range_criteria_list) > 0 and len(value_criteria_list) > 0:
                to_delete = np.random.choice(
                    [c for c in ["range", "value"] if len(candidate[c]) > 0]
                )
                remove_criterium(candidate[to_delete])
            elif len(range_criteria_list) > 0:
                to_delete = np.random.choice(
                    [c for c in ["range"] if len(candidate[c]) > 0]
                )
                remove_criterium(candidate[to_delete])
            elif len(value_criteria_list) > 0:
                to_delete = np.random.choice(
                    [c for c in ["value"] if len(candidate[c]) > 0]
                )
                remove_criterium(candidate[to_delete])
            candidate["growth"] = crud.utils.get_growth(candidate, db)
            candidates = candidates.append(candidate, ignore_index=True)
        candidates = candidates.sort_values(by="growth", ascending=False).iloc[
            : OPTIMIZE_PARAMS["population"]
        ]
        range_criteria_list, value_criteria_list, bool_criteria_list = candidates[
            ["range", "value", "bool"]
        ].iloc[0]
        out_string = crud.utils.get_criteria_string(
            range_criteria_list, value_criteria_list, bool_criteria_list
        )

    end_growth = crud.utils.get_growth(out_string, db)
    improvement = end_growth - start_growth

    out = schemas.users.ScreenerOptimized.parse_obj(
        {"criteria": out_string, "improvement": improvement}
    )
    return out


def change_range_criterium(range_criteria_list):
    criterium = range_criteria_list.pop(np.random.randint(len(range_criteria_list)))
    criterium[1] = criterium[1] * np.random.uniform(
        1 - OPTIMIZE_PARAMS["delta_per_iter"], 1 + OPTIMIZE_PARAMS["delta_per_iter"]
    )
    criterium[2] = criterium[2] * np.random.uniform(
        1 - OPTIMIZE_PARAMS["delta_per_iter"], 1 + OPTIMIZE_PARAMS["delta_per_iter"]
    )
    range_criteria_list.append(criterium)


def remove_criterium(criteria_list):
    criteria_list.pop(np.random.randint(len(criteria_list)))
