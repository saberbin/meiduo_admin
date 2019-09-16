
def jwt_response_payload_handler(token, user, request):
    return {
        "token": token,
        "username": user.username,
        "user_id": user.id
    }
