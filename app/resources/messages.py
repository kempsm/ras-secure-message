from flask_restful import Resource
from flask import request
from flask import jsonify
from app.domain_model.domain import Message
from app.repository.saver import Saver
from app.repository.retriever import Retriever
import logging

logger = logging.getLogger(__name__)

"""Rest endpoint for message resources. Messages are immutable, they can only be created and archived."""


class MessageList(Resource):

    """Return a list of messages for the user"""
    @staticmethod
    def get():
        # res = authenticate(request)
        res = {'status': "ok"}
        if res == {'status': "ok"}:
            message_service = Retriever()
            # msg_list = message_service.retrieve_message_list()
            resp = message_service.retrieve_message_list()
            resp.status_code = 200
            return resp
        else:
            return res


class MessageSend(Resource):

    """Send message for a user"""
    @staticmethod
    def post():
        #res = authenticate(request)
        res = {'status': "ok"}
        if res == {'status': "ok"}:
            logger.info("Message send POST request.")
            message_json = request.get_json()
            message = Message(message_json['to'], message_json['from'], message_json['body'])
            message_service = Saver()
            message_service.save_message(message)
            resp = jsonify({'status': "ok"})
            resp.status_code = 200
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
