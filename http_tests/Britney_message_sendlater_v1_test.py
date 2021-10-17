import pytest
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from http_tests.route_wrappers_test import *

# InputError when any of:
      
#         Channel ID is not a valid channel
#         Message is more than 1000 characters
#         Time sent is a time in the past
      
# AccessError when :
      
#         the authorised user has not joined the channel they are trying to post to

# Parameters:(token, channel_id, message, time_sent)
# Return Type:{ message_id }

# message_sendlater_v1()

# Send a message from authorised_user to the channel specified by channel_id automatically at a specified time in the future

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def crt_channel():
    def _create_channel(token):
        return channels_create_v2(token, 'channel_1', True)
    return _create_channel


@pytest.fixture
def message_text():
    def _message_text(num):
        return f"Test message {num}."
    return _message_text

@pytest.fixture
def InputError():
    return 400

@pytest.fixture
def AccessError():
    return 403

# common case
def test_common(reg_user, crt_channel, message_text):
    clear_v2()
    token = reg_user(0)['token']
    channel_id = crt_channel(token)['channel_id']

    dt = datetime.now(timezone.utc) + timedelta(hours=0, minutes=0, seconds=1)  
    time_sent = dt.replace(tzinfo=timezone.utc).timestamp()

    # message_id = message_sendlater_v1(token, channel_id, message_text(0), time_sent)['message_id']
    # message = channel_messages_v2(user_token, channel_id, 0)['messages'][0]
    # assert message['message_id'] == message_id
    # assert message['message'] == message_text(0)

    assert message_sendlater_v1(token, channel_id, message_text(0), time_sent)['message_id'] == 0
    prev_message_id = message_send_v2(token, channel_id, message_text(1))['message_id']
    assert message_sendlater_v1(token, channel_id, message_text(2), time_sent)['message_id'] == prev_message_id + 1


# Channel ID is not a valid channel
def test_invaild_channel(reg_user, crt_channel, message_text, InputError):
    clear_v2()
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    message = message_text(0)

    dt = datetime.now(timezone.utc) + timedelta(hours=0, minutes=0, seconds=1)  
    time_sent = dt.replace(tzinfo=timezone.utc).timestamp()

    message_sendlater_request = message_sendlater_v1(user_token, channel_id + 1, message, time_sent)
    assert message_sendlater_request.status_code == InputError


# Message is more than 1000 characters
def test_long_message(reg_user, crt_channel, message_text, InputError):
    clear_v2()
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    message = 'a' * 1001

    dt = datetime.now(timezone.utc) + timedelta(hours=0, minutes=0, seconds=1)  
    time_sent = dt.replace(tzinfo=timezone.utc).timestamp()

    message_sendlater_request = message_sendlater_v1(user_token, channel_id, message, time_sent)
    assert message_sendlater_request.status_code == InputError

# Time sent is a time in the past
def test_time_past(reg_user, crt_channel, message_text, InputError):
    clear_v2()
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    message = message_text(0)

    dt = datetime.now(timezone.utc) - timedelta(hours=9, minutes=50) 
    time_sent = dt.replace(tzinfo=timezone.utc).timestamp()

    message_sendlater_request = message_sendlater_v1(user_token, channel_id, message, time_sent)
    assert message_sendlater_request.status_code == InputError

# the authorised user has not joined the channel they are trying to post to
def test_sender_non_channel_member(reg_user, crt_channel, message_text, AccessError):
    clear_v2()
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    user_token_1 = reg_user(1)['token']
    message = message_text(0)

    dt = datetime.now(timezone.utc) + timedelta(hours=0, minutes=0, seconds=1)  
    time_sent = dt.replace(tzinfo=timezone.utc).timestamp()

    message_sendlater_request = message_sendlater_v1(user_token_1, channel_id, message, time_sent)
    assert message_sendlater_request.status_code == AccessError


# invalid_token
def test_invalid_token(reg_user, crt_channel, message_text, AccessError):
    
    clear_v2()
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    message = message_text(0)

    dt = datetime.now(timezone.utc) + timedelta(hours=0, minutes=0, seconds=1)  
    time_sent = dt.replace(tzinfo=timezone.utc).timestamp()
    
    message_sendlater_request = message_sendlater_v1("Invalid token", channel_id, message, time_sent)
    assert message_sendlater_request.status_code == AccessError