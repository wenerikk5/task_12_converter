from app import db
from app.models import User


def test_valid_registration(client, init_db):
    """
    GIVEN an app configured for testing
    WHEN the '/get-token' is requested (POST)
    THEN check the User is created, response includes id and token
    """
    response = client.post('/get-token?name=John')
    assert response.status_code == 200
    assert db.session.query(User).count() == 3
    assert b'id' in response.data
    assert b'token' in response.data


def test_incorrect_registration(client, init_db):
    """
    GIVEN an app configured for testing
    WHEN the '/get-token' is requested (POST)
    THEN check the User is created, response includes id and token
    """
    response = client.post('/get-token')
    assert response.status_code == 400
    assert db.session.query(User).count() == 2
    assert b'message' in response.data
    assert b'token' not in response.data


def test_valid_authentication(client, init_db):
    """
    GIVEN an app configured for testing
    WHEN the '/get-records' is requested (GET)
    THEN check User is verified
    """
    headers = {
        'Authorization': 'Bearer token1',
        "id": "1111"
    }
    response = client.get('/get-records', headers=headers)
    assert response.status_code == 200
    assert b'records' in response.data


def test_update_token(client, init_db):
    """
    GIVEN an app configured for testing
    WHEN the '/update-token' is requested (POST)
    THEN check User's token is updated
    """
    data = {
        "id": "1111",
        "token": "token1"
    }
    response = client.post('/update-token', json=data)
    user1 = db.session.query(User).filter_by(id='1111').first()
    assert response.status_code == 200
    assert user1.token != '1111'
    assert b'token' in response.data
