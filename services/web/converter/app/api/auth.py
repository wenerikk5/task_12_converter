from flask_httpauth import HTTPTokenAuth
from flask import jsonify, request

from app import db
from app.api import bp
from app.models import User
from app.api.errors import error_response, bad_request

token_auth = HTTPTokenAuth(scheme='Bearer')


@bp.route('/get-token', methods=['POST'])
def get_token():
    """
    Register User in DB based on received "name".
    Generates and returns unique User ID and UUID token.
    """
    # Name might be received via request args or in body.
    try:
        name = request.get_json().get('name')
    except:
        name = request.args.get('name') or {}

    if not name:
        return bad_request('Для регистрации требуется имя пользователя "name"')

    token, exp = User.get_token()
    user = User(
        id=User.generate_id(),
        name=name,
        token=token,
        token_expiration=exp,
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'token': token})


@bp.route('/update-token', methods=['POST'])
def update_token():
    """
    Update token (valid or expired) based on User ID and
    last token, which presents in DB.
    """
    error = False
    try:
        user_id = request.get_json().get('id')
        user_token = request.get_json().get('token')
        if not user_id or not user_token:
            raise Exception
    except:
        error = True

    if error:
        return bad_request('Пожалуйста, предоставьте идентификатор '
                           'пользователя и последний токен.')

    try:
        user = User.query.filter_by(id=user_id).first()
        new_token = user.update_token(user_token)
        if not new_token:
            raise Exception
    except:
        return bad_request('Пожалуйста, предоставьте корректный идентификатор '
                           'пользователя и последний токен.')
    db.session.commit()
    return jsonify({'id': user.id, 'token': new_token})


@token_auth.verify_token
def verify_token(token: str):
    """Function for login required decorator."""

    id = request.form.get('id') or request.headers.get('id', {})

    if not id:
        return None
    return User.check_token(id, token)


@token_auth.error_handler
def token_auth_error(status: int):
    """If fail token verification."""

    return error_response(status, 'Неавторизованный запрос')
