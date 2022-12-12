from sqlalchemy import Boolean, Column, Integer, String

from app.db.base import Base


class RangeCriterium(Base):
    __tablename__ = "rangecriterium"
    screenerId = Column(Integer, primary_key=True)
    name = Column(String)
    minVal = Column(Integer)
    maxVal = Column(Integer)


class ValueCriterium(Base):
    __tablename__ = "valuecriterium"
    screenerId = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(String)
    inverted = Column(Boolean)


class BoolCriterium(Base):
    __tablename__ = "boolcriterium"
    screenerId = Column(Integer, primary_key=True)
    name = Column(String)
    included = Column(Boolean)
