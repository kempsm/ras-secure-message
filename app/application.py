import logging
from logging.config import dictConfig

from flask import Flask, request
from flask import jsonify
from flask_restful import Api

from app import settings
from app.exception.exceptions import MessageSaveException
from app.repository import database
from app.resources.health import Health, DatabaseHealth, HealthDetails
from app.resources.messages import MessageList, MessageSend, MessageById, ModifyById
from app.resources.drafts import Drafts
from werkzeug.exceptions import BadRequest

# initialise logging defaults for project
logging_config = dict(
        version=1,
        disable_existing_loggers=False,
        formatters={
            'f': {'format': '%(asctime)s %(levelname)s %(name)s %(message)s'}
        },
        handlers={
            'h': {'class': 'logging.StreamHandler',
                  'formatter': 'f',
                  'level': settings.SMS_LOG_LEVEL}
        },
        root={
            'handlers': ['h'],
            'level': settings.SMS_LOG_LEVEL,
        },
    )

dictConfig(logging_config)
# set werkzeug logging level
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(level=settings.SMS_WERKZEUG_LOG_LEVEL)

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SECURE_MESSAGING_DATABASE_URL
app.config['SQLALCHEMY_POOL_SIZE'] = settings.SQLALCHEMY_POOL_SIZE
app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(settings.APP_LOG_LEVEL)
database.db.init_app(app)

logger = logging.getLogger(__name__)
logger.info('Starting application')


def drop_database():
    database.db.drop_all()

with app.app_context():
    database.db.create_all()
    database.db.session.commit()

api.add_resource(Health, '/health')
api.add_resource(DatabaseHealth, '/health/db')
api.add_resource(HealthDetails, '/health/details')
api.add_resource(MessageList, '/messages')
api.add_resource(MessageSend, '/message/send')
api.add_resource(MessageById, '/message/<message_id>')
api.add_resource(ModifyById, '/message/<message_id>/modify')
api.add_resource(Drafts, '/draft/save')


@app.before_request
def before_request():
    if request.endpoint is not None and 'health' not in request.endpoint and 'user_urn' not in request.headers:
            raise (BadRequest(description="User URN required to access this Microservice Resource"))


@app.errorhandler(MessageSaveException)
def handle_save_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
