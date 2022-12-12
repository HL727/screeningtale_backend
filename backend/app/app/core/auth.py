from app.config import settings
from app.models.users import User
from authlib.integrations.starlette_client import OAuth
from passlib.hash import pbkdf2_sha256
from starlette.config import Config


class UserAuth:

    @classmethod
    def get_password_hash(cls, password: str):
        return pbkdf2_sha256.hash(password)

    @classmethod
    def verify_password(cls, db, email: str, password: str):
        user = db.query(User).filter_by(email=email).first()

        if user and pbkdf2_sha256.verify(password, user.password):
            return user


# Google oauth
oauth = OAuth(Config(environ={
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
}))

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)
