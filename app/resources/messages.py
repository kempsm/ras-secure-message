from flask_restful import Resource
from flask import request
from flask import jsonify
from app.domain_model.domain import Message
from app.repository.saver import Saver
from structlog import get_logger
from app.authentication.authenticator import authenticate

logger = get_logger()

"""Rest endpoint for message resources. Messages are immutable, they can only be created and archived."""


class MessageList(Resource):

    """Return a list of messages for the user"""
    @staticmethod
    def get():
        resp = jsonify({'status': "ok"})
        resp.status_code = 200
        return resp


class MessageSend(Resource):

    """Send message for a user"""
    @staticmethod
    def post():
        #res = authenticate(request)
        res = {'status': "ok"}
        if res == {'status': "ok"}:
            logger.info("Hit post message send endpoint")
            message_json = request.get_json()
            message = Message(message_json['to'], message_json['from'], message_json['body'])
            message_service = Saver()
            message_service.save_message(message)
            resp = jsonify({'status': "ok"})
            resp.status_code = 200
            logger.info("Receive response" + str(resp))
            return resp
        else:
            return res


class MessageById(Resource):

    """Get message by id"""
    @staticmethod
    def get(message_id):
        #res = authenticate(request)
        res = {'status': "ok"}
        if res == {'status': "ok"}:
            resp = jsonify({"status": "ok", "message_id": message_id})
            resp.status_code = 200
            return resp
        else:
            return res

    """Update message by id"""
    @staticmethod
    def put():
        resp = jsonify({"status": "ok"})
        resp.status_code = 200
        return resp
