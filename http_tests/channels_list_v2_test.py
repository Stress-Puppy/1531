import pytest

from http_tests.route_wrappers_test import *

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def crt_channel():
    def _create_channel(token, num, is_public):
        return channels_create_v2(token, f'channel_{num}', is_public)
    return _create_channel

@pytest.fixture
def ch_name():
    def _channel_name(num):
        return f'channel_{num}'
    return _channel_name

@pytest.fixture
def AccessError():
    return 403

def test_single_channel(reg_user, crt_channel, ch_name):
    clear_v2()
    auth_user_token = reg_user(0)['token']

    channel_name = ch_name(0)

    channel_id = crt_channel(auth_user_token, 0, True)['channel_id']

    channel_list = channels_list_v2(auth_user_token)['channels']

    assert len(channel_list) == 1
    assert channel_list[0]['channel_id'] == channel_id
    assert channel_list[0]['name'] == channel_name

def test_multiple_channels(reg_user, crt_channel, ch_name):
    clear_v2()
    auth_user_token = reg_user(0)['token']

    expected_channels = []
    for i in range(5):
        channel_id = crt_channel(auth_user_token, i, True)['channel_id']
        channel_name = ch_name(i)
        expected_channel = { 'channel_id' : channel_id, 'name' : channel_name}
        expected_channels.append(expected_channel)

    channel_list = channels_list_v2(auth_user_token)['channels']

    assert channel_list == expected_channels

def test_non_channel_owner(reg_user, crt_channel, ch_name):
    clear_v2()
    auth_user_token = reg_user(0)['token']
    basic_user_token = reg_user(1)['token']

    channel_name = ch_name(0)

    channel_id = crt_channel(auth_user_token, 0, True)['channel_id']

    channel_join_v2(basic_user_token, channel_id)

    channel_list = channels_list_v2(basic_user_token)['channels']

    assert len(channel_list) == 1
    assert channel_list[0]['channel_id'] == channel_id
    assert channel_list[0]['name'] == channel_name

def test_multiple_users_multiple_channels(reg_user, crt_channel, ch_name):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2_token = reg_user(1)['token']

    expected_channels_1 = []
    for i in range(5):
        channel_id = crt_channel(user_1_token, i, True)['channel_id']
        channel_name = ch_name(i)
        expected_channel = { 'channel_id' : channel_id, 'name' : channel_name}
        expected_channels_1.append(expected_channel)

    expected_channels_2 = []
    for i in range(5,10):
        channel_id = crt_channel(user_2_token, i, True)['channel_id']
        channel_name = ch_name(i)
        expected_channel = { 'channel_id' : channel_id, 'name' : channel_name}
        expected_channels_2.append(expected_channel)

    channel_list_1 = channels_list_v2(user_1_token)['channels']
    channel_list_2 = channels_list_v2(user_2_token)['channels']

    assert channel_list_1 == expected_channels_1
    assert channel_list_2 == expected_channels_2

def test_user_not_in_channel(reg_user):
    clear_v2()
    auth_user_token = reg_user(0)['token']

    channel_list = channels_list_v2(auth_user_token)['channels']

    assert len(channel_list) == 0
    
def test_invalid_token(reg_user, AccessError):
    clear_v2()
    reg_user(0)['token']
    list_request = channels_list_v2("Invalid token")
    assert list_request.status_code == AccessError

