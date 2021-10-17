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
def crt_dm():
    def _create_dm(token, u_id):
        return dm_create_v1(token, u_id)
    return _create_dm

@pytest.fixture
def send_message():
    def _send_message(token, ch_id):
        return message_send_v2(token, ch_id, "Test")
    return _send_message

@pytest.fixture
def send_dm_message():
    def _send_message(token, dm_id):
        return message_senddm_v1(token, dm_id, "Test")
    return _send_message

@pytest.fixture
def InputError():
    return 400

@pytest.fixture
def AccessError():
    return 403

def test_remove_single_channel_message(reg_user, crt_channel, send_message):
    clear_v2()
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    message_id = send_message(user_token, channel_id)['message_id']
    message_remove_v1(user_token, message_id)
    messages = channel_messages_v2(user_token, channel_id, 0)['messages']
    assert not len(messages)

def test_remove_multiple_channel_messages(reg_user, crt_channel, send_message):
    clear_v2()
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    message_ids = []
    for i in range(0,10):
        message_id = send_message(user_token, channel_id)['message_id']
        message_ids.append(message_id)
    for i in range(0,len(message_ids)-1):
        message_remove_v1(user_token, message_ids[i])
        messages = channel_messages_v2(user_token, channel_id, 0)['messages']
        for msg in messages:
            assert message_ids[i] != msg['message_id']
    message_remove_v1(user_token, message_ids[-1])
    messages = channel_messages_v2(user_token, channel_id, 0)['messages']
    assert not len(messages)

def test_remove_single_dm_message(reg_user, crt_dm, send_dm_message):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2_id = reg_user(1)['auth_user_id']
    dm_id = crt_dm(user_1_token, [user_2_id])['dm_id']
    message_id = send_dm_message(user_1_token, dm_id)['message_id']
    message_remove_v1(user_1_token, message_id)
    messages = dm_messages_v1(user_1_token, dm_id, 0)['messages']
    assert not len(messages)

def test_remove_multiple_dm_messages(reg_user, crt_dm, send_dm_message):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2_id = reg_user(1)['auth_user_id']
    dm_id = crt_dm(user_1_token, [user_2_id])['dm_id']
    message_ids = []
    for i in range(0,10):
        message_id = send_dm_message(user_1_token, dm_id)['message_id']
        message_ids.append(message_id)
    for i in range(0,len(message_ids)-1):
        message_remove_v1(user_1_token, message_ids[i])
        messages = dm_messages_v1(user_1_token, dm_id, 0)['messages']
        for msg in messages:
            assert message_ids[i] != msg['message_id']
    message_remove_v1(user_1_token, message_ids[-1])
    messages = dm_messages_v1(user_1_token, dm_id, 0)['messages']
    assert not len(messages)

def test_remove_removed_message(reg_user, crt_channel, send_message, InputError):
    clear_v2()
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    message_id = send_message(user_token, channel_id)['message_id']
    message_remove_v1(user_token, message_id)
    remove_request = message_remove_v1(user_token, message_id)
    assert remove_request.status_code == InputError

def test_nonexistent_message_id(reg_user, crt_channel, send_message, InputError):
    clear_v2()
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    message_id = send_message(user_token, channel_id)['message_id']
    remove_request = message_remove_v1(user_token, message_id+1)
    assert remove_request.status_code == InputError

def test_non_owner_remove_message_of_other_user(reg_user, crt_channel, send_message, AccessError):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2_token = reg_user(1)['token']
    channel_id = crt_channel(user_1_token)['channel_id']
    channel_join_v2(user_2_token, channel_id)
    message_id = message_send_v2(user_1_token, channel_id, "Test")['message_id']
    remove_request = message_remove_v1(user_2_token, message_id)
    assert remove_request.status_code == AccessError

def test_channel_owner_remove_message_of_other_user(reg_user, crt_channel, send_message):
    clear_v2()
    user_1_token = reg_user(0)['token']
    user_2_token = reg_user(1)['token'] # Channel owner
    channel_id = crt_channel(user_2_token)['channel_id']
    channel_join_v2(user_1_token, channel_id)
    message_id = send_message(user_1_token, channel_id)['message_id']
    message_remove_v1(user_2_token, message_id)
    messages = channel_messages_v2(user_2_token, channel_id, 0)['messages']
    assert not len(messages)

def test_dreams_owner_remove_message_of_other_user(reg_user, crt_channel, send_message):
    clear_v2()
    user_1_token = reg_user(0)['token'] # Dreams owner
    user_2_token = reg_user(1)['token'] 
    channel_id = crt_channel(user_1_token)['channel_id']
    channel_join_v2(user_2_token, channel_id)
    message_id = send_message(user_2_token, channel_id)['message_id']
    message_remove_v1(user_1_token, message_id)
    messages = channel_messages_v2(user_1_token, channel_id, 0)['messages']
    assert not len(messages)

def test_invalid_token(reg_user, crt_channel, send_message, AccessError):
    clear_v2()
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    message_id = send_message(user_token, channel_id)['message_id']
    remove_request = message_remove_v1("Invalid token", message_id)
    assert remove_request.status_code == AccessError
