import re

from pydantic import BaseModel, ValidationError, validator


class ScreenersBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Screeners(ScreenersBase):
    criteria: str


class ScreenersNames(ScreenersBase):
    criteria: str


class ScreenersCagr(BaseModel):
    criteria: str
    cagr: float


class ScreenersMatches(BaseModel):
    criteria: str
    matches: int

    class Config:
        orm_mode = True


class ScreenerCriteria(BaseModel):
    criteria: str

    class Config:
        orm_mode = True


class ScreenerDB(ScreenersBase):
    userid: int


class ScreenerOptimized(ScreenerCriteria):
    improvement: float


class GetUserPasswordSchema(BaseModel):
    email: str
    password: str

    @validator('email')
    def email_validator(email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            raise ValueError('Invalid email address')
        return email


class ResetPasswordSchema(BaseModel):
    token: str
    password1: str
    password2: str

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError('passwords do not match')
        return v


class EmailSchema(BaseModel):
    email: str

    @validator('email')
    def email_validator(email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(regex, email):
            raise ValueError('Invalid email address')
        return email