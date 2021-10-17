import pytest

from http_tests.route_wrappers_test import *

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
def InputError():
    return 400

@pytest.fixture
def AccessError():
    return 403

'''
Sending a message to get buffered in the standup queue, assuming a standup is currently active

Parameters:(token, channel_id, message)
Return Type:{}

InputError when any of:
    Channel ID is not a valid channel
    Message is more than 1000 characters (not including the username and colon)
    An active standup is not currently running in this channel
AccessError when
    The authorised user is not a member of the channel that the message is within
'''

# common case
def test_common_case(reg_user, crt_channel):
    clear_v2()

    token = reg_user(0)['token']

    channel_id = crt_channel(token)['channel_id']
    standup_length = 1
    standup_start_v1(token, channel_id, standup_length)
    
    assert standup_send_v1(token, channel_id, 'HELLOWORLD') == {}
    assert standup_send_v1(token, channel_id, 'PYTHON') == {}

# other member in the channel case
def test_other_menber_case(reg_user, crt_channel):
    clear_v2()

    token = reg_user(0)['token']
    user1 = reg_user(1)
    token1 = user1['token']
    u_id = user1['auth_user_id']

    channel_id = crt_channel(token)['channel_id']
    channel_invite_v2(token, channel_id, u_id)
    standup_length = 1
    standup_start_v1(token, channel_id, standup_length)
    
    assert standup_send_v1(token1, channel_id, 'HELLOWORLD') == {}
    assert standup_send_v1(token1, channel_id, 'PYTHON') == {}

# The authorised user is not a member of the channel that the message is within
def test_not_correct_channel_number(reg_user, crt_channel, AccessError):
    clear_v2()

    token0 = reg_user(0)['token']
    token1 = reg_user(1)['token']
    channel_id1 = crt_channel(token1)['channel_id']
    standup_length = 1
    standup_start_v1(token1, channel_id1, standup_length)

    standup_send_request = standup_send_v1(token0, channel_id1, 'helloworld')
    assert standup_send_request.status_code == AccessError

# An active standup is not currently running in this channel
def test_not_active_standup(reg_user, crt_channel, InputError):
    clear_v2()

    token = reg_user(0)['token']

    channel_id = crt_channel(token)['channel_id']

    standup_send_request = standup_send_v1(token, channel_id, 'helloworld')
    assert standup_send_request.status_code == InputError


# Message is more than 1000 characters (not including the username and colon)
def test_long_messge(reg_user, crt_channel, InputError):
    clear_v2()

    token = reg_user(0)['token']

    channel_id = crt_channel(token)['channel_id']
    message = 'a' * 1001
    standup_length = 1
    standup_start_v1(token, channel_id, standup_length)

    standup_send_request = standup_send_v1(token, channel_id, message)
    assert standup_send_request.status_code == InputError

# Channel ID is not a valid channel
def test_invalid_channel_id(reg_user, crt_channel, InputError):
    clear_v2()

    token = reg_user(0)['token']

    channel_id = crt_channel(token)['channel_id']
    standup_length = 1
    standup_start_v1(token, channel_id, standup_length)

    standup_send_request = standup_send_v1(token, channel_id + 1, 'helloworld')
    assert standup_send_request.status_code == InputError

# the given token is invaild
def test_invalid_token(reg_user, crt_channel, AccessError):
    clear_v2()

    token = reg_user(0)['token']

    channel_id = crt_channel(token)['channel_id']
    standup_length = 1
    standup_start_v1(token, channel_id, standup_length)

    standup_send_request = standup_send_v1("Invalid token", channel_id, 'helloworld')
    assert standup_send_request.status_code == AccessError
