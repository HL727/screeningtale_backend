from sqlalchemy import func
from sqlalchemy.orm.session import Session

from app.crud.crud_utils import utils
from app.models import Screener
from app import models


class CRUDUsers:
    def get_user_by_id(self, user_id: int, db: Session) -> models.User:
        return db.query(models.User).filter(models.User.id == user_id).first()

    def add_screener(self, user_id: int, name_insert: str, q: str, db: Session):
        utils.validate_criteria_string(q)
        res = (
            db.query(Screener)
            .filter(Screener.creator_id == user_id, Screener.name == name_insert)
            .one_or_none()
        )
        if res:
            res.criteria = q
            db.commit()
            return res
        else:
            screener: Screener = Screener(
                name=name_insert, creator_id=user_id, criteria=q
            )
            db.add(screener)
            db.commit()
            return screener

    def get_screeners(self, user_id: int, db: Session):
        screeners = (
            db.query(Screener.id, Screener.name, Screener.criteria)
            .filter(Screener.creator_id == user_id)
            .all()
        )
        return screeners

    def delete_screener(self, screener_id: int, user: models.User, db: Session):
        if (
            db.query(models.Screener.creator_id)
            .filter(models.Screener.id == screener_id)
            .one()[0]
            == user.id
        ):
            db.query(Screener).filter(Screener.id == screener_id).delete()
            db.commit()
            return True
        return False

    def get_users(self, db: Session):
        return db.query(models.User).all()


users = CRUDUsers()
