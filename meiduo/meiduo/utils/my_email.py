from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSeiralizer
from django.conf import settings
from users.models import User


def generate_verify_url(user):
    serializer = TJWSSeiralizer(secret_key=settings.SECRET_KEY, expires_in=600)  # 10min

    data = {
        "user_id": user.id,
        "email": user.email
    }
    token = serializer.dumps(data)
    verify_url = "%s?token=%s" % (settings.EMAIL_VERIFY_URL, token.decode())
    # print(verify_url)
    return verify_url


def decode_token(token):
    serializer = TJWSSeiralizer(secret_key=settings.SECRET_KEY, expires_in=300)  # 5min
    try:
        data = serializer.loads(token)
        user_id = data.get("user_id")
        user = User.objects.get(id=user_id)
    except Exception as e:
        return None
    # return the user
    return user
