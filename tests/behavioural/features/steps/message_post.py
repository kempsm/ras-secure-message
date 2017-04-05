import flask
import nose.tools
from behave import given, then, when
from app import application
import datetime
from unittest import mock
from app.common.alerts import AlertUser, AlertViaGovNotify

url = "http://localhost:5050/message/send"
headers = {'Content-Type': 'application/json'}
data = {}


def before_scenario(context):
    AlertUser.alertMethod = mock.Mock(AlertViaGovNotify)
    data.update({'msg_to': 'Richard',
                 'msg_from': 'Torrance',
                 'subject': 'Hello World',
                 'body': 'Test',
                 'thread': '?',
                 'create_date': datetime.datetime.now(datetime.timezone.utc),
                 'read_date': datetime.datetime.now(datetime.timezone.utc)})


@given('a valid message')
def step_impl_code(context):
    before_scenario(context)


@when('it is sent')
def step_impl(context):
    context.response = application.app.test_client().post(url, data=flask.json.dumps(data), headers=headers)


@then('a 201 HTTP response is returned')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 201)


@given('a message with an empty "To" field')
def step_impl_code(context):
    data['msg_to'] = ''


# @when('it is sent a')
# def step_impl(context):
#     context.execute_steps("when it is sent")


@then('a 400 HTTP response is returned')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 400)


@given('a message with an empty "From" field')
def step_impl(context):
    data['msg_from'] = ''


# @when('it is sent')
# def step_impl(context):
#     context.execute_steps("when it is sent")


@then('a 400 HTTP response is returned as the response afterwards')
def step_impl(context):
    context.execute_steps("then a 400 HTTP response is returned")


@given('a message with an empty "Body" field')
def step_impl(context):
    data['body'] = ''


# @when('it is sent')
# def step_impl(context):
#     context.execute_steps("when it is sent")


@then('a 400 HTTP response is returned as a response after')
def step_impl(context):
    context.execute_steps('then a 400 HTTP response is returned')


@given('a message with an empty "Subject" field')
def step_impl(context):
    data['subject'] = ""


# @when('it is sent')
# def step_impl(context):
#     context.execute_steps("when it is sent")


@then('a 400 HTTP response is returned as a response')
def step_impl(context):
    context.execute_steps('then a 400 HTTP response is returned')


@given('a message is sent with an empty "Thread ID"')
def step_impl(context, ):
    before_scenario(context)


# @when('it is sent')
# def step_impl(context):
#     context.execute_steps("when it is sent")


@then('a 201 status code is the response')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 201)


@given('a message is marked as archived')
def step_impl(context):
    data['archived'] = 'True'


# @when('it is sent')
# def step_impl(context):
#     context.execute_steps("when it is sent")


@then('a 201 response is received')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 201)


@given('a message is marked as read')
def step_impl(context):
    data['marked_as_read'] = 'True'


# @when('it is sent')
# def step_impl(context):
#     context.execute_steps("when it is sent")


@then('a 201 response is acquired')
def step_impl(context):
    nose.tools.assert_equal(context.response.status_code, 201)


if __name__ == '__main__':
    from behave import __main__ as behave_executable
    behave_executable.main(None)