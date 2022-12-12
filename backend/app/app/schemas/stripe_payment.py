from pydantic import BaseModel


class StripeSessionURL(BaseModel):
    url: str

    class Config:
        orm_mode = True


class PaymentParam(BaseModel):
    price_id: str
    url_success: str
    url_cancel: str


class CustomerParam(BaseModel):
    customer_id: str
    return_url: str


class EmailCustomerParam(BaseModel):
    email: str
    return_url: str


class PriceModel(BaseModel):
    elite_price: float
    premium_price: float
    elite_price_id: str
    premium_price_id: str


class Subscriptions(BaseModel):
    object: str
    data: list
    has_more: bool
    total_count: int
    url: str

    class Config:
        orm_mode = True


class Customer(BaseModel):
    id: str
    object: str
    email: str
    invoice_prefix: str
    name: str
    subscriptions: Subscriptions

    class Config:
        orm_mode = True
