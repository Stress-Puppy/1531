import pytest

from http_tests.route_wrappers_test import *
from time import sleep

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
For a given channel, return whether a standup is active in it, and what time the standup 
finishes. If no standup is active, then time_finish returns None

Parameters:(token, channel_id)
Return Type:{ is_active, time_finish }

InputError when any of:
    Channel ID is not a valid channel
'''

def test_no_active_standup(reg_user, crt_channel):
    clear_v2()

    token = reg_user(0)['token']

    channel_id = crt_channel(token)['channel_id']

    standup_info = standup_active_v1(token, channel_id)

    assert not standup_info['is_active']
    assert standup_info['time_finish'] == None

def test_active_standup(reg_user, crt_channel):
    clear_v2()

    token = reg_user(0)['token']

    channel_id = crt_channel(token)['channel_id']

    standup_length = 5
    finish_time = standup_start_v1(token, channel_id, standup_length)['time_finish']

    standup_info = standup_active_v1(token, channel_id)

    assert standup_info['is_active']
    assert standup_info['time_finish'] == finish_time

def test_standup_inactive_after_ending(reg_user, crt_channel):
    clear_v2()

    token = reg_user(0)['token']

    channel_id = crt_channel(token)['channel_id']

    standup_length = 1
    standup_start_v1(token, channel_id, standup_length)
    sleep(standup_length)

    standup_info = standup_active_v1(token, channel_id)

    assert not standup_info['is_active']
    assert standup_info['time_finish'] == None

def test_invalid_channel_id(reg_user, crt_channel, InputError):
    clear_v2()

    token = reg_user(0)['token']

    channel_id = crt_channel(token)['channel_id']

    standup_length = 1
    standup_start_v1(token, channel_id, standup_length)

    active_request = standup_active_v1(token, channel_id+1)
    assert active_request.status_code == InputError

def test_invalid_token(reg_user, crt_channel, AccessError):
    clear_v2()

    token = reg_user(0)['token']

    channel_id = crt_channel(token)['channel_id']

    standup_length = 1
    standup_start_v1(token, channel_id, standup_length)

    active_request = standup_active_v1("Invalid token", channel_id)
    assert active_request.status_code == AccessError