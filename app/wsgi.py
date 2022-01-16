"""Web Server Gateway Interface"""

import logging.config
from sqlalchemy import inspect
from sqlalchemy.orm import scoped_session
from sqlalchemy_utils import database_exists, create_database
from flask import Flask, jsonify, make_response, request, Response
from settings import __version__, __all_func__
from settings import broker_url, result_backend, logger_config
from database import SessionLocal, engine
from example_db_init import init_db
from main import get_devices, check_status, _create_task
from decorators import auth


SUCCESS_RESPONSE = {"status": "success", "msg": "OK", "api_version": __version__}
FAILED_RESPONSE = {"status": "error", "api_version": __version__}
VERSION_API = "v1.0"

app = Flask(__name__)
app.session = scoped_session(SessionLocal)
app.config.update(
    JSON_AS_ASCII=False,
    CELERY_BROKER_URL=broker_url,
    result_backend=result_backend
)

# Logging settings
logging.config.dictConfig(logger_config)
logger = logging.getLogger('CApi')


@app.before_first_request
def create_db() -> None:
    """
     Makes db schema and populates it with initial data
    """

    # Check, if example db and tables are not exists, create them.
    if not database_exists(engine.url):
        create_database(engine.url)
    inspector = inspect(engine)
    if not "devices" in inspector.get_table_names():
        init_db()


@app.route(f'/api/{VERSION_API}/functions', methods=["GET"])
@auth
def get_functions() -> tuple | Response:
    """Returns all available requests"""

    SUCCESS_RESPONSE['data'] = __all_func__
    return make_response(jsonify(SUCCESS_RESPONSE), 200)


@app.route(f'/api/{VERSION_API}/devices', methods=["GET"])
@auth
def load_devices() -> tuple | Response:
    """Returns all devices available for configuration"""

    SUCCESS_RESPONSE['data'] = get_devices(app.session)
    return make_response(jsonify(SUCCESS_RESPONSE), 200)


@app.route(f'/api/{VERSION_API}/execute', methods=["POST"])
@auth
def execute() -> tuple | Response:
    """Starts async process of configuration and returns task_id immediately"""
    from tasks import async_execute  # pylint: disable=import-outside-toplevel

    try:
        if request.json.get("id") and request.json.get("command"):
            task_data = _create_task(app.session, request.json["id"], request.json["command"])
            task_id = task_data.task_id
            async_execute.apply_async(args=[request.json, task_id],
                                      task_id=str(task_id))
            SUCCESS_RESPONSE["data"] = {"task_id": task_id}
            return make_response(jsonify(SUCCESS_RESPONSE), 201)
        FAILED_RESPONSE["msg"] = "Please pass the required parameters:" \
                                 " id (device id) and command"
        return make_response(jsonify(FAILED_RESPONSE), 400)
    except AttributeError as error:
        print(error)
        FAILED_RESPONSE["msg"] = "Please pass the parameters in JSON format"
        return make_response(jsonify(FAILED_RESPONSE), 400)


@app.route(f'/api/{VERSION_API}/status', methods=["GET"])
@auth
def get_status() -> tuple | Response:
    """Gets current configuration task status"""

    if request.json:
        params = request.json
    elif request.args:
        params = request.args
    else:
        FAILED_RESPONSE["msg"] = "Please pass the parameters in JSON format or in query string"
        return make_response(jsonify(FAILED_RESPONSE), 400)

    if params.get("task_id"):
        SUCCESS_RESPONSE['data'] = check_status(app.session, int(params.get('task_id')))
        return make_response(jsonify(SUCCESS_RESPONSE), 200)
    FAILED_RESPONSE["msg"] = "Please pass the required parameters: task_id"
    return make_response(jsonify(FAILED_RESPONSE), 400)


if __name__ == '__main__':
    app.run(debug=True, port=7500, threaded=True)
