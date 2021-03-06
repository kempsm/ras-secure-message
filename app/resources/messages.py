# from app.authentication.jwt import decode
from flask_restful import Resource
from flask import request, jsonify, json
from werkzeug.exceptions import BadRequest
from json import load
from app.repository.modifier import Modifier
from app.validation.domain import MessageSchema
from app.repository.saver import Saver
from app.repository.retriever import Retriever
from app.repository.database import Status
import logging
from app.common.alerts import AlertUser
from app import settings
from app.settings import MESSAGE_QUERY_LIMIT
from app.validation.labels import Labels
from app.validation.user import User
from datetime import timezone, datetime

logger = logging.getLogger(__name__)

MESSAGE_LIST_ENDPOINT = "messages"
MESSAGE_BY_ID_ENDPOINT = "message"

"""Rest endpoint for message resources. Messages are immutable, they can only be created."""


class MessageList(Resource):
    """Return a list of messages for the user"""

    @staticmethod
    def get():
        # res = authenticate(request)
        res = {'status': "ok"}
        if res == {'status': "ok"}:
            page = 1
            limit = MESSAGE_QUERY_LIMIT

            if request.args.get('limit') and request.args.get('page'):
                page = int(request.args.get('page'))
                limit = int(request.args.get('limit'))

            message_service = Retriever()
            status, result = message_service.retrieve_message_list(page, limit)
            if status:
                resp = MessageList._paginated_list_to_json(result, page, limit, request.host_url,
                                                           request.headers.get('user_urn'))
                resp.status_code = 200
                return resp
        else:
            return res

    @staticmethod
    def _paginated_list_to_json(paginated_list, page, limit, host_url, user_urn):
        """used to change a pagination object to json format with links"""
        messages = {}
        msg_count = 0
        for message in paginated_list.items:
            msg_count += 1
            msg = message.serialize(user_urn)
            msg['_links'] = {"self": {"href": "{0}{1}/{2}".format(host_url, MESSAGE_BY_ID_ENDPOINT, msg['msg_id'])}}
            messages["{0}".format(msg_count)] = msg

        links = {
            'first': {"href": "{0}{1}".format(host_url, "messages")},
            'self': {"href": "{0}{1}?page={2}&limit={3}".format(host_url, MESSAGE_LIST_ENDPOINT, page, limit)}
        }

        if paginated_list.has_next:
            links['next'] = {
                "href": "{0}{1}?page={2}&limit={3}".format(host_url, MESSAGE_LIST_ENDPOINT, (page + 1), limit)}

        if paginated_list.has_prev:
            links['prev'] = {
                "href": "{0}{1}?page={2}&limit={3}".format(host_url, MESSAGE_LIST_ENDPOINT, (page - 1), limit)}

        return jsonify({"messages": messages, "_links": links})


class MessageSend(Resource):
    """Send message for a user"""

    def post(self):
        """used to handle POST requests to send a message"""
        logger.info("Message send POST request.")
        post_data = request.get_json()
        is_draft = False
        draft_id = None
        if 'msg_id' in post_data:
            is_draft = MessageSend().check_if_draft(post_data['msg_id'])
            if is_draft is True:
                draft_id = post_data['msg_id']
                post_data['msg_id'] = ''
            else:
                raise (BadRequest(description="Message can not include msg_id"))

        message = MessageSchema().load(post_data)

        if message.errors == {}:
            return self.message_save(message, is_draft, draft_id)
        else:
            res = jsonify(message.errors)
            res.status_code = 400
            return res

    @staticmethod
    def check_if_draft(message_id):
        """Checks if the message is in the message table with a DRAFT label"""
        db_model = Status()
        result = db_model.query.filter_by(msg_id=message_id, label=Labels.DRAFT.value).first()
        if result is None:
            return False
        else:
            return True

    @staticmethod
    def del_draft_labels(draft_id):
        modifier = Modifier()
        modifier.del_draft(draft_id)

    def message_save(self, message, is_draft, draft_id):
        """Saves the message to the database along with the subsequent status and audit"""
        save = Saver()
        save.save_message(message.data, datetime.now(timezone.utc))
        if User(message.data.urn_from).is_respondent:
            save.save_msg_status(message.data.urn_from, message.data.msg_id, Labels.SENT.value)
            save.save_msg_status(message.data.survey, message.data.msg_id, Labels.INBOX.value)
            save.save_msg_status(message.data.survey, message.data.msg_id, Labels.UNREAD.value)
        else:
            save.save_msg_status(message.data.survey, message.data.msg_id, Labels.SENT.value)
            save.save_msg_audit(message.data.msg_id, message.data.urn_from)
            save.save_msg_status(message.data.urn_to, message.data.msg_id, Labels.INBOX.value)
            save.save_msg_status(message.data.urn_to, message.data.msg_id, Labels.UNREAD.value)

        if is_draft is True:
            self.del_draft_labels(draft_id)
        return MessageSend._alert_recipients(message.data.msg_id)

    @staticmethod
    def _alert_recipients(reference):
        """used to alert user once messages have been saved"""
        recipient_email = settings.NOTIFICATION_DEV_EMAIL  # TODO change this when know more about party service
        alert_user = AlertUser()
        alert_status, alert_detail = alert_user.send(recipient_email, reference)
        resp = jsonify({'status': '{0}'.format(alert_detail), 'msg_id': reference})
        resp.status_code = alert_status
        return resp


class MessageById(Resource):
    """Get and update message by id"""

    @staticmethod
    def get(message_id):
        """Get message by id"""
        # res = authenticate(request)
        user_urn = request.headers.get('user_urn')  # getting user urn from header request
        # check user is authorised to view message
        message_service = Retriever()
        # pass msg_id and user urn
        resp = message_service.retrieve_message(message_id, user_urn)
        return jsonify(resp)


class ModifyById(Resource):
    """Update message status by id"""

    @staticmethod
    def put(message_id):
        """Update message by status"""
        user_urn = request.headers.get('user_urn')

        request_data = request.get_json()

        action, label = ModifyById.validate_request(request_data)

        # pass msg_id and user urn
        message = Retriever().retrieve_message(message_id, user_urn)

        if label == Labels.UNREAD.value:
            resp = ModifyById.modify_unread(action, message, user_urn)
        else:
            resp = ModifyById.modify_label(action, message, user_urn, label)

        if resp:
            res = jsonify({'status': 'ok'})
            res.status_code = 200

        else:
            res = jsonify({'status': 'error'})
            res.status_code = 400
        return res

    @staticmethod
    def modify_label(action, message, user_urn, label):
        """Adds or deletes a label"""
        label_exists = label in message
        if action == 'add' and not label_exists:
            return Modifier.add_label(label, message, user_urn)
        if label_exists:
            return Modifier.remove_label(label, message, user_urn)
        else:
            return False

    @staticmethod
    def modify_unread(action, message, user_urn):
        if action == 'add':
            return Modifier.add_unread(message, user_urn)
        return Modifier.del_unread(message, user_urn)

    @staticmethod
    def validate_request(request_data):
        """Used to validate data within request body for ModifyById"""
        if 'label' not in request_data:
            raise BadRequest(description="No label provided")

        label = request_data["label"]
        if label not in Labels.label_list.value:
            raise BadRequest(description="Invalid label provided: {0}".format(label))

        if label not in [Labels.ARCHIVE.value, Labels.UNREAD.value]:
            raise BadRequest(description="Non modifiable label provided: {0}".format(label))

        if 'action' not in request_data:
            raise BadRequest(description="No action provided")

        action = request_data["action"]
        if action not in ["add", "remove"]:
            raise BadRequest(description="Invalid action requested: {0}".format(action))

        return action, label
