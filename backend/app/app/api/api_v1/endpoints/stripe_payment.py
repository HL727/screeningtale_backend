import logging
from typing import Optional

import stripe
from aioredis import Redis
from app import crud, schemas
from app.api.dependencies import get_current_user, get_redis
from app.config import settings
from app.db.session import session_scope
from app.models.users import MemberDefinition, User
from app.utils.api_route_classes.ratelimit import RateLimitAPIRoute
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import update

router = APIRouter(route_class=RateLimitAPIRoute)
stripe.api_key = settings.STRIPE_API_KEY_LIVE


@router.post(
    "/subscribe",
    response_model=schemas.StripeSessionURL,
)
def get_payment_url(
    payment_param: schemas.PaymentParam, user: User = Depends(get_current_user)
):
    try:
        session: stripe.checkout.Session = crud.pay_stripe(
            get_stripe_id(payment_param.price_id),
            payment_param.url_success,
            payment_param.url_cancel,
            user,
        )
        response = schemas.StripeSessionURL.parse_obj({"url": session.url})
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/unsubscribe",
)
async def unsubscribe(user: User = Depends(get_current_user), redis: Redis = Depends(get_redis)):
    try:
        stripe.Subscription.delete(user.subscription_id)
        key = f"token:{user.id}"
        await redis.delete(key)

        return {"msg": "Unsubscribed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


def get_stripe_id(price_name: str):
    if price_name == "premium":
        return "price_1JNej4DTz3cLSfZ9aqzN8xIr"
    elif price_name == "elite":
        return "price_1KyLNXDTz3cLSfZ9MWVJAWa7"
    elif price_name == "premium_annual":
        return "price_1KydNeDTz3cLSfZ9Gs8zILiJ"
    elif price_name == "elite_annual":
        return "price_1L3i2ODTz3cLSfZ96btSh0N0"
    else:
        return None


def set_subscription(
    email: str, price_id: Optional[str] = None, subscription_id=None
):
    stripe_price_to_member_role = {
        "price_1JNej4DTz3cLSfZ9aqzN8xIr": MemberDefinition.PREMIUM,
        "price_1KydNeDTz3cLSfZ9Gs8zILiJ": MemberDefinition.PREMIUM,
        "price_1KyLNXDTz3cLSfZ9MWVJAWa7": MemberDefinition.ELITE,
        "price_1L3i2ODTz3cLSfZ96btSh0N0": MemberDefinition.ELITE,
    }

    with session_scope() as db:
        member_role = stripe_price_to_member_role.get(
            price_id, MemberDefinition.FREE
        )

        db.execute(
            update(User)
            .where(User.email == email)
            .values(
                {
                    "member_role": member_role,
                    "subscription_id": subscription_id,
                }
            )
        )


# @router.get("/price_models", response_model=schemas.PriceModel)
# def get_price_models(request: Request):

#     model1 = schemas.PriceModel(
#         elite_price=19.95,
#         premium_price=2.95,
#         elite_price_id="price_1JNeiHDTz3cLSfZ9d5si2zLo",
#         premium_price_id="price_1JT1AZDTz3cLSfZ9U8NL2Zuz",
#     )

#     model2 = schemas.PriceModel(
#         elite_price=19.95,
#         premium_price=4.95,
#         elite_price_id="price_1JNeiHDTz3cLSfZ9d5si2zLo",
#         premium_price_id="price_1JT1AMDTz3cLSfZ97rw5RFM3",
#     )

#     model3 = schemas.PriceModel(
#         elite_price=19.95,
#         premium_price=9.95,
#         elite_price_id="price_1JNeiHDTz3cLSfZ9d5si2zLo",
#         premium_price_id="price_1JNej4DTz3cLSfZ9aqzN8xIr",
#     )

#     models = [model1, model2, model3]
#     ip_array = np.array(request.client.host.split("."))
#     ip_array = ip_array.astype(np.int16)
#     seed = ip_array[0]

#     np.random.seed(seed)
#     price_model: schemas.PriceModel = np.random.choice(models)
#     return price_model


@router.get("/customer_by_id/{customer_id}", response_model=schemas.Customer)
def get_customer_by_id(customer_id: str):
    try:
        customer = stripe.Customer.retrieve(customer_id, expand=["subscriptions"])
        out = schemas.Customer.from_orm(customer)
        return out
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/customer_portal_by_id", response_model=schemas.StripeSessionURL)
def get_customer_portal_by_id(customer_param: schemas.CustomerParam):
    try:
        session: stripe.billing_portal.Session = crud.create_customer_session(
            customer_param.customer_id, customer_param.return_url
        )
        return schemas.StripeSessionURL.parse_obj({"url": session.url})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/customer_by_email/{customer_email}", response_model=schemas.Customer)
def get_customer_by_email(customer_email: str):
    try:
        customer_list = stripe.Customer.list(
            email=customer_email, expand=["data.subscriptions"]
        )["data"]
        if len(customer_list) >= 1:
            customer = customer_list[0]
            out = schemas.Customer.from_orm(customer)
            return out
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No user with email '{customer_email}'",
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_customer_id_by_email(customer_email: str):
    try:
        customer_list = stripe.Customer.list(
            email=customer_email
        )["data"]
        if len(customer_list) >= 1:
            customer = customer_list[0]
            out = schemas.Customer.from_orm(customer)
            return out.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No user with email '{customer_email}'",
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/customer_portal_by_email", response_model=schemas.StripeSessionURL)
def get_customer_portal_by_email(customer_param: schemas.EmailCustomerParam):
    try:
        logger.info("astarts")
        logger.info(customer_param)
        logger.info(customer_param.email)
        id = get_customer_id_by_email(customer_param.email)
        logger.info("cussr")
        session: stripe.billing_portal.Session = crud.create_customer_session(
            id, customer_param.return_url
        )
        logger.info(session)
        return schemas.StripeSessionURL.parse_obj({"url": session.url})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/webhook")
async def webhook_handler(
    request: Request,
    stripe_signature: str = Header(None),
    redis: Redis = Depends(get_redis),
):

    try:
        data = await request.body()
        event = stripe.Webhook.construct_event(
            payload=data,
            sig_header=stripe_signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )

        event_data = event["data"]
        event_type = event["type"]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if event_type == "checkout.session.completed":
        # Payment is successful and the subscription is created.
        # You should provision the subscription and save the customer ID to your database.
        await redis.set(
            f"user:{event_data['object']['customer_details']['email']}",
            f"id:{event_data['object']['customer']}",
        )

    elif event_type == "invoice.payment_succeeded":
        # Get user by email
        # Change the member role of user based on subscription
        try:
            email = event_data["object"]["customer_email"]
            price_id = event_data["object"]["lines"]["data"][0]["plan"]["id"]
            subscription_id = event_data["object"]["subscription"]
            customer_id = event_data["object"]["customer"]

            with session_scope() as db:
                user = db.query(User).filter_by(email=email).first()
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User does not exist",
                    )
                elif user.subscription_id and subscription_id != user.subscription_id:
                    stripe.Subscription.delete(user.subscription_id)

                key = f"token:{user.id}"
                await redis.delete(key)
                set_subscription(email, price_id, subscription_id)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    elif event_type == "invoice.payment_failed":
        # The payment failed or the customer does not have a valid payment method.
        # The subscription becomes past_due. Notify your customer and send them
        # to the customer portal to update their payment information.
        print(event_type)
        print(event_data)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Payment failed"
        )

    elif event_type == "customer.subscription.updated":
        # Get user by email
        # Change the member role of user if subscription ends
        try:
            email = stripe.Customer.retrieve(event_data["object"]["customer"]).get(
                "email"
            )
            subscription_id = event_data["object"]["id"]

            if event_data["object"]["status"] == "unpaid":
                # delete subscription
                set_subscription(email, None, None, None)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    elif event_type == "customer.subscription.deleted":
        # Get user by email
        # Change the member role of user if subscription ends
        try:
            subscription_id = event_data["object"]["id"]

            with session_scope() as db:
                # delete subscription
                db.execute(
                    update(User)
                    .where(User.subscription_id == event_data["object"]["id"])
                    .values(
                        {
                            "member_role": MemberDefinition.FREE,
                            "subscription_id": None
                        }
                    )
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    else:
        print("Unhandled event type {}".format(event_type))
