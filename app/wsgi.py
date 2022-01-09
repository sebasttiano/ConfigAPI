"""Web Server Gateway Interface"""

import logging.config
from flask import Flask, jsonify, make_response, request, Response
from settings import __version__, __all_func__, config, logger_config
from database import SessionLocal
from example_db_init import init_db
from sqlalchemy.orm import scoped_session
from functions.main import get_devices, execute_command, check_status
from decorators import auth

SUCCESS_RESPONSE = {"status": "success", "msg": "OK", "api_version": __version__}
FAILED_RESPONSE = {"status": "error", "api_version": __version__}
VERSION_API = "v1.0"

app = Flask(__name__)
app.session = scoped_session(SessionLocal)
app.config["JSON_AS_ASCII"] = False

# Loading approved ip
allowed_ips = config.get("Main", "WhiteIPS").replace(" ", "").split(",")

# Logging settings
logging.config.dictConfig(logger_config)
logger = logging.getLogger('CApi')


@app.before_first_request
def create_db() -> None:
    """
     Makes db schema and populates it with initial data
    """
    init_db()


@app.before_request
def check_remote_addr() -> Response:
    """
    Handler for check remote ip. Return 403 fobbiden, if remote ip not found in
    configuration file config.ini.
    Returns:
        HTTP response with json
    """

    if request.remote_addr not in allowed_ips:
        message = f"Access with ip address {request.remote_addr} is forbidden"
        logger.error(message)
        FAILED_RESPONSE["msg"] = message
        return make_response(jsonify(FAILED_RESPONSE), 403)


@app.route(f'/api/{VERSION_API}/functions', methods=["GET"])
@auth
def get_functions() -> tuple| Response:
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
    """Starts process of configuration and returns task_id"""

    try:
        if request.json.get("id") and request.json.get("command"):
            task_id = execute_command(app.session, request.json)
            SUCCESS_RESPONSE["data"] = {"task_id": task_id}
            return make_response(jsonify(SUCCESS_RESPONSE), 201)
        else:
            FAILED_RESPONSE["msg"] = "Please pass the required parameters: id (device id) and command"
            return make_response(jsonify(FAILED_RESPONSE), 400)
    except AttributeError:
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
    else:
        FAILED_RESPONSE["msg"] = "Please pass the required parameters: task_id"
        return make_response(jsonify(FAILED_RESPONSE), 400)


if __name__ == '__main__':
    app.run(debug=True, port=7500, threaded=True)

