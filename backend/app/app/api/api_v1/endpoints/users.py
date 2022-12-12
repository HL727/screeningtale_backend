import random
import string
from datetime import datetime, timedelta
from typing import List

from app import crud, models, schemas
from app.api.dependencies import get_current_user, get_db
from app.config import settings
from app.core.auth import UserAuth, oauth
from app.schemas.users import EmailSchema
from app.utils.api_route_classes.ratelimit import RateLimitAPIRoute
from app.utils.auth import create_access_token
from app.worker import app as celery_app
from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.requests import Request

router = APIRouter(route_class=RateLimitAPIRoute)


@router.post(
    "/save_screener",
    status_code=201,
    response_model=schemas.users.ScreenerDB,
)
def save_screeners_view(
    name: str,
    q: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = crud.utils.get_screener_count(user.id, db)
    if count >= 20:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't have more than 20 screeners",
        )
    screener = crud.users.add_screener(user.id, name, q, db)
    out = schemas.users.ScreenerDB.parse_obj(
        {"id": screener.id, "name": screener.name, "userid": screener.creator_id}
    )
    return out


@router.get("/screeners", response_model=List[schemas.users.Screeners])
def screeners_view(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    screeners = crud.users.get_screeners(user.id, db)
    # screeners_out_list: List[schemas.users.Screeners] = []
    # for screener_db in screeners_from_db:
    #     screener = schemas.users.ScreenersBase.from_orm(screener_db)
    #     criteria = crud.utils.get_string_representation_for_criteria(screener.id, db)[0]
    #     cagr = 100 * (crud.utils.get_growth(criteria, db, annualized=True) - 1)
    #     matches = crud.utils.get_count(criteria, db)

    #     screener_out = schemas.users.Screeners.parse_obj(
    #         {**screener.dict(), "criteria": criteria, "cagr": cagr, "matches": matches}
    #     )
    #     screeners_out_list.append(screener_out)
    return screeners


@router.get(
    "/criteria_id_to_string/{screener_id}",
    response_model=schemas.users.ScreenerCriteria,
)
def string_representation_view(
    screener_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if any(screener.id == screener_id for screener in user.screeners):
        criteria = crud.utils.get_string_representation_for_criteria(screener_id, db)[0]
        criteria_out = schemas.users.ScreenerCriteria.parse_obj({"criteria": criteria})
        return criteria_out
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"User '{user.name}' is not the owner of screener with id '{screener_id}'",
    )


@router.delete("/delete_screener/{screener_id}", status_code=204, response_model=None)
def delete_screener(
    screener_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        if not crud.users.delete_screener(screener_id, user, db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error due to your access token and access token of screener owner not matching",
            )
        return {}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error when retrieving screener. There may not be a screener with id '{screener_id}'",
        )


# Authentication endpoints
@router.post("/login", status_code=200, response_model=None)
def login_user(
    login_user_schema: schemas.GetUserPasswordSchema,
    db: Session = Depends(get_db),
):
    user_auth = UserAuth()
    user = user_auth.verify_password(
        db, email=login_user_schema.email, password=login_user_schema.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "subscription": user.member_role,
        "email_verified_status": user.email_verified_status,
        "token_type": "bearer",
        "expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    }


@router.post("/register", status_code=200, response_model=None)
def create_user(
    create_user_schema: schemas.GetUserPasswordSchema, db: Session = Depends(get_db)
):
    try:
        user_auth = UserAuth()

        user = db.query(models.User).filter_by(email=create_user_schema.email)

        if user.first():
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            )

        verify_token = "".join(
            random.choices(
                string.ascii_lowercase + string.ascii_uppercase + string.digits, k=25
            )
        )

        user = models.User(
            email=create_user_schema.email,
            password=user_auth.get_password_hash(create_user_schema.password),
        )

        db.add(user)
        db.commit()

        verify_token_obj = models.VerificationToken(user=user.id, token=verify_token)
        db.add(verify_token_obj)
        db.commit()

        celery_app.send_task(
            "app.worker.send_mail.send_verification_mail",
            args=[create_user_schema.email, verify_token],
            priority=1,
        )

        return {"status_code": status.HTTP_200_OK, "msg": "Signup successful"}
    except Exception as err:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error when creating user: { err }",
        )


@router.post("/get_current_user", status_code=200, response_model=None)
def get_authenticated_user(user: models.User = Depends(get_current_user)):
    return {
        "email": user.email,
        "subscription": user.member_role,
        "email_verified_status": user.email_verified_status
    }


# Email verification and reset password endpoints
@router.get("/verify_email", status_code=200, response_model=None)
def verify_user(token: str, db: Session = Depends(get_db)):
    try:
        token_obj = db.query(models.VerificationToken).filter_by(token=token).first()

        if not token_obj:
            return RedirectResponse(f"{ settings.FRONTEND_URL }/token-invalid")

        user_id = token_obj.user
        db.query(models.User).filter_by(id=user_id).update(
            {"email_verified_status": True, "email_verified": datetime.now()}
        )

        db.delete(token_obj)
        db.commit()

        return RedirectResponse(f"{ settings.FRONTEND_URL }/verify")

    except Exception as err:
        print(f"Error in verifying {str(err)}")
        RedirectResponse(f"{ settings.FRONTEND_URL }/")


@router.post("/send_verification_mail", status_code=200, response_model=None)
def send_verification_token(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    verify_token = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=25))

    if user.email_verified_status:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already verified",
        )

    verify_token_obj = db.query(models.VerificationToken).filter_by(user=user.id)

    if verify_token_obj.first():
        verify_token_obj.update({"token": verify_token})
    else:
        db.add(models.VerificationToken(user=user.id, token=verify_token))

    db.commit()

    celery_app.send_task(
        "app.worker.send_mail.send_verification_mail",
        args=[user.email, verify_token],
        priority=1,
    )

    return {"msg": "Verification mail sent"}


@router.post("/reset_password", status_code=200, response_model=None)
def reset_password(
    reset_password_schema: schemas.ResetPasswordSchema, db: Session = Depends(get_db)
):
    try:
        token_obj = (
            db.query(models.PasswordResetToken)
            .filter_by(token=reset_password_schema.token)
            .first()
        )

        if not token_obj:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token invalid or expired",
            )

        user_id = token_obj.user

        user = db.query(models.User).filter_by(id=user_id).first()

        if user:
            update_args = {
                "password": UserAuth().get_password_hash(
                    reset_password_schema.password1
                )
            }

            if not user.email_verified_status:
                update_args["email_verified_status"] = True
                update_args["email_verified"] = datetime.now()

            db.query(models.User).filter_by(id=user_id).update(update_args)

        db.delete(token_obj)
        db.commit()
        return {"msg": "Password reset successful"}

    except Exception as err:
        return {"msg": "Error in verifying password reset request", "err": str(err)}


@router.post(
    "/send_password_reset_verification_mail", status_code=200, response_model=None
)
def send_password_reset_verification_token(
    email_schema: EmailSchema, db: Session = Depends(get_db)
):
    try:
        email = email_schema.email
        user = db.query(models.User).filter_by(email=email).first()

        if user:
            reset_token = "".join(
                random.choices(
                    string.ascii_lowercase + string.ascii_uppercase + string.digits,
                    k=25,
                )
            )

            reset_token_obj = db.query(models.PasswordResetToken).filter_by(
                user=user.id
            )

            if reset_token_obj.first():
                reset_token_obj.update({"token": reset_token})
            else:
                db.add(models.PasswordResetToken(user=user.id, token=reset_token))

            db.commit()

            celery_app.send_task(
                "app.worker.send_mail.send_password_reset_confirmation_mail",
                args=[email, reset_token],
                priority=0,
            )

        return {"msg": "Password reset confirmation mail sent"}

    except Exception as err:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in sending password reset confirmation mail: { err }",
        )


# Third party auth
@router.get("/google_login")
async def google_login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth")
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ error }",
        )
    user = token.get("userinfo")
    user_obj = db.query(models.User).filter_by(email=user["email"]).first()

    if not user_obj:
        user_auth = UserAuth()
        user_obj = models.User(
            name=user["name"],
            email=user["email"],
            password=user_auth.get_password_hash(
                "".join(
                    random.choices(
                        string.ascii_lowercase + string.ascii_uppercase + string.digits,
                        k=25,
                    )
                )
            ),
            image=user["picture"],
            email_verified_status=True,
        )

        db.add(user_obj)
        db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_obj.id)}, expires_delta=access_token_expires
    )

    return RedirectResponse(
        f"{ settings.FRONTEND_URL }/api/setToken?token={ access_token }\
            &token_type=access_token&expires_in_minutes={settings.ACCESS_TOKEN_EXPIRE_MINUTES}"
    )
