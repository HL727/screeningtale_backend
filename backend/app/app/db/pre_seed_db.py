import logging
from typing import List

from celery.result import AsyncResult
from sqlalchemy.orm import Session

from app import models
from app.utils.tickers import get_backtest_tickers

from app.worker import app as celery_app

logger = logging.getLogger(__name__)

# BACKTEST_TICKERS = [
#     "002159.SZ",
#     "CEM",
#     "1926.T",
#     "JM2.DE",
#     "LNG",
#     "0680.HK",
#     "0577.HK",
#     "QLIRO.ST",
#     "JETPAK.ST",
#     "AACIU",
#     "CRSAW",
#     "IDIP.PA",
#     "ALAVY.PA",
#     "MITA",
#     "GBOX",
#     "ATA.PA",
#     "BSIG",
#     "NRSN",
#     "NELCAST.NS",
#     "VLS.L",
#     "600648.SS",
#     "NUVA",
#     "NRIX",
#     "ATI",
#     "AKX.DE",
#     "PRSR",
#     "4335.HK",
#     "PHUNW",
#     "TTR1.DE",
#     "THAC",
#     "CS.ST",
#     "PEL.NS",
#     "CUEN",
#     "002051.SZ",
#     "0472.HK",
#     "KXS.TO",
#     "8163.TW",
#     "1YD.DE",
#     "EME.L",
#     "7751.T",
#     "K",
#     "PAG",
#     "KOLTEPATIL.NS",
#     "GLAXO.NS",
#     "SD",
#     "TRG.ST",
#     "FCIT.L",
#     "EDIT",
#     "JNEO.L",
#     "2191.T",
#     "WEAT",
#     "QUIS.V",
#     "ISAT.JK",
#     "336370.KS",
#     "GDEN",
#     "4028.T",
#     "RSG.L",
#     "002860.SZ",
#     "INDEX.ST",
#     "EXPE",
#     "3535.TW",
#     "NRXP",
#     "6191.T",
#     "000952.SZ",
#     "UFO.L",
#     "3800.HK",
#     "000725.SZ",
#     "ALSIM.PA",
#     "8476.HK",
# ]


def init_db(db: Session, add_h_tick: bool = True) -> None:

    if False:
        historicals: List[models.Historical] = db.query(models.Historical).distinct(
            models.Historical.ticker
        )
        all_historicals = get_backtest_tickers()
        existing_historicals = [historical.ticker for historical in historicals]
        tickers = [t for t in all_historicals if t not in existing_historicals]
        for ticker in tickers:
            celery_app.send_task(
                "app.worker.insert_historical.insert_historical",
                args=[ticker, None, 10],
                priority=6,
            )
        # This isn't necessary at every restart. Do it manually instead.
        # celery_app.send_task(
        #     "app.worker.insert_historical.cluster_historical",
        #     args=[],
        # )
        logger.info("Added historical tickers.")
    logger.info("Pre seeding complete.")


# -------------------------------------------------------------------------------------
# The code below was an attempt to handle several tickers in batch, to parallellize API calls. Even a batch size as small as 2 gave aiohttp.client_exceptions.ContentTypeError.
# Leaving code in case we want to reattempt this approach at a later time.

# def init_db(db: Session, add_h_tick: bool = True) -> None:

#     if add_h_tick:
#         historicals: List[models.Historical] = db.query(models.Historical).distinct(
#             models.Historical.ticker
#         )
#         existing_historicals = [historical.ticker for historical in historicals]
#         tickers = [t for t in BACKTEST_TICKERS if t not in existing_historicals]
#         ticker_batches = batch_tickers(tickers, batch_size=2)
#         for ticker_batch in ticker_batches:
#             celery_app.send_task(
#                 "app.worker.insert_historical.insert_historical_batch",
#                 args=[ticker_batch],
#             )
#         logger.info("Added historical tickers.")
#     logger.info("Pre seeding complete.")
