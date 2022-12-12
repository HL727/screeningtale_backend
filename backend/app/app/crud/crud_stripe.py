import stripe
from app.db.session import session_scope
from app.models.users import User
from sqlalchemy import update


def pay_stripe(price_id, url_success, url_cancel, user):
    if not user.customer_id:
        with session_scope() as db:
            customer = stripe.Customer.create(
                email= user.email,
            )
            db.execute(
                update(User).where(User.id == user.id).values(
                    {"customer_id" : customer["id"],}
                )
            )

    session = stripe.checkout.Session.create(
        success_url=url_success,
        cancel_url=url_cancel,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        customer=user.customer_id,
    )

    return session


def create_customer_session(customer_id, return_url):
    session = stripe.billing_portal.Session.create(
        customer=customer_id, return_url=return_url
    )

    return session
