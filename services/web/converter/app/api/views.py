import time
import os
import uuid
import shutil

from io import BytesIO

from flask import jsonify, request, current_app, send_file
from werkzeug.utils import secure_filename

from pydub import AudioSegment

from app import db
from app.api import bp
from app.models import Record
from app.api.auth import token_auth
from app.api.errors import error_response, bad_request


@bp.route('/record', methods=['POST'])
@token_auth.login_required
def upload():
    """
    Upload file in .wav format, convert it in .mp3 and save
    in DB (as bytes). Generate link to download file from DB.
    """

    length = request.content_length
    upload_folder = current_app.config['UPLOAD_FOLDER']
    error = ''

    if 'file' not in request.files:
        msg = 'Запрос не содержит файла с полем "file"'
        return bad_request(msg)

    file = request.files['file']

    if file and allowed_file(file.filename, length):
        filename = secure_filename(file.filename)[:50]
        file.save(os.path.join(upload_folder, filename))

        try:
            convert_wav_mp3(upload_folder, filename)
        except:
            # File may have wrong extension name or is corrupted.
            clean_upload_folder(upload_folder)
            return bad_request('Файл не имеет формат "wav" или поврежден!')

        sound = open(
            os.path.join(upload_folder, rename_to_mp3(filename)),
            'rb'
        )

        record = Record(
            id=str(uuid.uuid4()),
            filename=rename_to_mp3(filename),
            data=sound.read(),
            user_id=token_auth.current_user().id
        )
        db.session.add(record)
        db.session.commit()
    else:
        error = 'Произошла ошибка по одной из следующих причин: ' \
                'файл отсутствует, имеет недопустимый размер ' \
                '(более 10 МБ) или недопустимое расширение.'

    clean_upload_folder(upload_folder)

    if error:
        return bad_request(error)
    return f"""
            Ссылка для загрузки mp3-файла:
            http://127.0.0.1/record?id={record.id}&user={record.user_id}
            """


@bp.route('/record', methods=['GET'])
def download():
    """Download record file from DB via link."""

    record_id = request.args.get('id')
    record = Record.query.filter_by(id=record_id).first()
    if not record:
        return error_response(404, 'Запрашиваемый файл не обнаружен.')
    # return send_file(BytesIO(record.data),
    #                  mimetype="audio/mpeg",
    #                  download_name=record.filename)
    return send_file(BytesIO(record.data),
                     mimetype="application/octet-stream",
                     download_name=record.filename)


@bp.route('/get-records', methods=['GET'])
@token_auth.login_required
def get_my_records():
    """List all records of User in DB."""

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    data = Record.to_collection_dict(
        token_auth.current_user().records,
        page,
        per_page,
        'api.get_my_records'
    )
    return jsonify(data)


def convert_wav_mp3(upload_folder: str, filename: str) -> None:
    """Convert .wav file to .mp3 by use pydub"""

    start = time.perf_counter()
    out_filename = rename_to_mp3(filename)
    AudioSegment.from_wav(os.path.join(upload_folder, filename)) \
                .export(os.path.join(upload_folder, out_filename),
                        format="mp3")
    finish = time.perf_counter()
    print(f"Продолжительность конвертации: {finish-start} с. ")


def allowed_file(filename: str, file_size: int) -> bool:
    """
    Check that file:
    - has .wav extension
    - not empty
    - do not exceed max allowable size (synchronize with nginx.conf settings)
    """
    allowed_extensions = ['wav']
    max_size_in_mb = 10

    # file_size received in bytes
    allowed_max_size = (file_size / 1024 / 1024) < max_size_in_mb
    allowed_min_size = file_size > 1
    allowed_extension = (secure_filename(filename).split('.')[-1]
                         in allowed_extensions)
    return all([allowed_extension, allowed_min_size, allowed_max_size])


def rename_to_mp3(filename: str) -> str:
    return '.'.join(filename.split('.')[:-1]) + '.mp3'


def clean_upload_folder(upload_folder: str) -> None:
    """
    Clean up upload folder after saving file in DB.
    """
    for root, dirs, files in os.walk(upload_folder):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
