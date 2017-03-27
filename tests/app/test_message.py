import unittest
import json
import app.constants
from datetime import datetime, timezone
from app.domain_model.domain import DomainMessage, MessageSchema


class MessageTestCase(unittest.TestCase):
    """Test case for Messages"""

    max_diff = None      # Needed as some of the strings are bigger than max_diff

    def setUp(self):
        """setup test environment"""
        self.domain_message = DomainMessage(**{'msg_to': 'richard', 'msg_from': 'torrance', 'subject': 'MyMessage',
                                            'body': 'hello', 'thread': "?", 'archived': False, 'marked_as_read': False,
                                               'create_date': datetime.now(timezone.utc),
                                               'read_date': datetime.now(timezone.utc)})

    def test_marshal_json(self):
        """marshaling message to json"""
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(sut.data == self.domain_message)

    def test_message(self):
        """creating domainMessage object"""
        now = datetime.now(timezone.utc)
        now_string = now.__str__()
        sut = DomainMessage('me', 'you', 'subject', 'body', '5', False, False, now, now)
        sut_str = repr(sut)
        expected = '<Message(msg_to=me msg_from=you subject=subject body=body thread=5 archived=False marked_as_read=False create_date={0} read_date={0})>'.format(now_string)
        self.assertEquals(sut_str, expected)

    def test_message_not_equal(self):
        """testing two different domainMessage objects are not equal"""
        now = datetime.now(timezone.utc)
        message1 = DomainMessage('1', '2', '3', '4', '5', False, False, now, now)
        message2 = DomainMessage('1', '33', '3', '4', '5', False, False, now, now)
        self.assertTrue(message1 != message2)

    def test_message_equal(self):
        """testing two same domainMessage objects are equal"""
        now = datetime.now(timezone.utc)
        message1 = DomainMessage('1', '2', '3', '4', '5', False, False, now, now)
        message2 = DomainMessage('1', '2', '3', '4', '5', False, False, now, now)
        self.assertTrue(message1 == message2)

    def test_valid_message_passes_validation(self):
        """marshaling a valid message"""
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(sut.errors == {})

    def test_msg_to_field_too_long_fails_validation(self):
        """marshalling message with msg_to field too long """
        self.domain_message.msg_to = "x" * (app.constants.MAX_TO_LEN + 1)
        expected_error = 'To field length must not be greater than {0}.'.format(app.constants.MAX_TO_LEN)
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['msg_to'])

    def test_msg_to_min_length_validation_false(self):
        """marshalling message with msg_to field too short """
        self.domain_message.msg_to = ''
        expected_error = 'To field not populated.'
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['msg_to'])

    def test_msg_to_field_in_json_causes_error(self):
        """marshalling message with not msg_to field"""
        message = {'msg_from': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_to': ['Missing data for required field.']})

    def test_msg_from_field_too_long_fails_validation(self):
        """marshalling message with msg_from field too long """
        self.domain_message.msg_from = "x" * (app.constants.MAX_FROM_LEN + 1)
        expected_error = 'From field length must not be greater than {0}.'.format(app.constants.MAX_FROM_LEN)
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['msg_from'])

    def test_msg_from_min_length_validation_false(self):
        """marshalling message with msg_from field too short """
        self.domain_message.msg_from = ""
        expected_error = 'From field not populated.'
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['msg_from'])

    def test_msg_from_required_validation_false(self):
        """marshalling message with no msg_from field """
        message = {'msg_to': 'torrance', 'body': 'hello'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'msg_from': ['Missing data for required field.']})

    def test_body_too_big_fails_validation(self):
        """marshalling message with body field too long """
        self.domain_message.body = "x" * (app.constants.MAX_BODY_LEN + 1)
        expected_error = 'Body field length must not be greater than {0}.'.format(app.constants.MAX_BODY_LEN)
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['body'])

    def test_missing_body_fails_validation(self):
        """marshalling message with no body field """
        message = {'msg_to': 'richard', 'msg_from': 'torrance', 'body': ''}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'body': ['Body field not populated.']})

    def test_body_field_missing_from_json_causes_error(self):
        """marshalling message with no body field """
        message = {'msg_to': 'torrance', 'msg_from': 'someone'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors == {'body': ['Missing data for required field.']})

    def test_missing_subject_field_does_not_cause_error(self):
        """marshalling message with no subject field """
        message = {'msg_to': 'torrance', 'msg_from': 'someone'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors != {'subject': ['Missing data for required field.']})

    def test_subject_field_too_long_causes_error(self):
        """marshalling message with subject field too long"""
        self.domain_message.subject = "x" * (app.constants.MAX_SUBJECT_LEN + 1)
        expected_error = 'Subject field length must not be greater than {0}.'.format(app.constants.MAX_SUBJECT_LEN)
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['subject'])

    def test_missing_thread_field_does_not_cause_error(self):
        """marshalling message with no thread field"""
        message = {'msg_to': 'torrance', 'msg_from': 'someone'}
        schema = MessageSchema()
        data, errors = schema.load(message)
        self.assertTrue(errors != {'thread': ['Missing data for required field.']})

    def test_thread_field_too_long_causes_error(self):
        """marshalling message with thread field too long"""
        self.domain_message.thread = "x" * (app.constants.MAX_THREAD_LEN + 1)
        expected_error = 'Thread field length must not be greater than {0}.'.format(app.constants.MAX_THREAD_LEN)
        sut = self.serialise_and_deserialize_message()
        self.assertTrue(expected_error in sut.errors['thread'])

    def serialise_and_deserialize_message(self):
        """serialising and deserializing message"""
        schema = MessageSchema()
        json_result = schema.dumps(self.domain_message)
        return schema.load(json.loads(json_result.data))
