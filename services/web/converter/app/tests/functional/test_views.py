from pathlib import Path
from app import db
from app.models import User, Record


resource = Path(__file__).parent.parent.parent.parent / "data"


def test_valid_record_post(client, init_db):
    """
    GIVEN an app configured for testing
    WHEN the '/record' is requested (POST) with file
    THEN check Record is created, download link is returned.
    """
    filename = 'wav1.wav'
    data = {
        "id": "1111",
        "file": (resource / filename).open("rb")
    }
    headers = {
        'Authorization': 'Bearer token1'
    }
    response = client.post(
        '/record',
        data=data,
        headers=headers,
        content_type="multipart/form-data"
    )
    record = db.session.query(Record).first()
    assert response.status_code == 200
    assert db.session.query(Record).count() == 1
    assert record.id != '1'
    assert b'http:' in response.data


def test_fake_file_post(client, init_db):
    """
    GIVEN an app configured for testing
    WHEN the '/record' is requested (POST) with file which is not '.wav'
    THEN check Record is not created, error arise.
    """
    filename = 'fake_wav.wav'
    data = {
        "id": "1111",
        "file": (resource / filename).open("rb")
    }
    headers = {
        'Authorization': 'Bearer token1'
    }
    response = client.post(
        '/record',
        data=data,
        headers=headers,
        content_type="multipart/form-data"
    )
    assert response.status_code == 400
    assert db.session.query(Record).count() == 0
    assert b'error' in response.data


def test_unauthorized_record_post(client, init_db):
    """
    GIVEN an app configured for testing
    WHEN the '/record' is requested (POST) with wrong credentials
    THEN check Record is not created, error arise.
    """
    filename = 'wav1.wav'
    data = {
        "id": "1111",
        "file": (resource / filename).open("rb")
    }
    headers = {
        'Authorization': 'Bearer token2'
    }
    response = client.post(
        '/record',
        data=data,
        headers=headers,
        content_type="multipart/form-data"
    )
    assert response.status_code == 401
    assert db.session.query(Record).count() == 0
    assert b'error' in response.data


def test_user_records_list(client, init_db):
    """
    GIVEN an app configured for testing
    WHEN the '/get-records' is requested (GET)
    THEN check response includes 1 record.
    """
    filename = 'wav1.wav'
    data = {
        "id": "1111",
        "file": (resource / filename).open("rb")
    }
    headers = {
        'Authorization': 'Bearer token1'
    }
    response_post = client.post(
        '/record',
        data=data,
        headers=headers,
        content_type="multipart/form-data"
    )
    assert response_post.status_code == 200
    assert db.session.query(Record).count() == 1
    data = {
        "id": "1111"
    }
    response_get = client.get(
        '/get-records',
        data=data,
        headers=headers
    )
    assert response_get.status_code == 200
    assert b'"total_items":1' in response_get.data
