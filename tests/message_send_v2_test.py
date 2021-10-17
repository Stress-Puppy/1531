import pytest

from src.auth import auth_register_v2
from src.channel import channel_messages_v2
from src.channels import channels_create_v2
from src.message import message_send_v2
from src.standup import standup_active_v1
from src.other import clear_v2
from src.error import InputError, AccessError

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
def send_message():
    def _send_message(token, ch_id, num):
        return message_send_v2(token, ch_id, f"Test message {num}.")
    return _send_message

@pytest.fixture
def standup_message():
    def _send_message(token, ch_id):
        return message_send_v2(token, ch_id, f"/standup 1")
    return _send_message

@pytest.fixture
def message_text():
    def _message_text(num):
        return f"Test message {num}."
    return _message_text

def test_single_message(reg_user, crt_channel, send_message, message_text):
    clear_v2()
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    message_id = send_message(user_token, channel_id, 0)['message_id']
    message = channel_messages_v2(user_token, channel_id, 0)['messages'][0]
    assert message['message_id'] == message_id
    assert message['message'] == message_text(0)

def test_multi_message(reg_user, crt_channel, send_message, message_text):
    clear_v2()
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    message_ids = []
    message_texts = []
    for i in range(5):
        message_id = send_message(user_token, channel_id, i)['message_id']
        message_ids.append(message_id)
        message_texts.append(message_text(i))
    messages = channel_messages_v2(user_token, channel_id, 0)['messages']
    messages.reverse() # Most recent message should now be last
    # Reverse for purpose of comparison
    for i in range(5):
        message = messages[i]
        assert message['message_id'] == message_ids[i]
        assert message['message'] == message_texts[i]

def test_message_exactly_one_thousand(reg_user, crt_channel, send_message):
    clear_v2()
    message_string = "a"*1000
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    message_id = message_send_v2(user_token, channel_id, message_string)['message_id']
    message = channel_messages_v2(user_token, channel_id, 0)['messages'][0]
    assert message['message_id'] == message_id
    assert message['message'] == message_string

def test_message_longer_than_one_thousand(reg_user, crt_channel):
    clear_v2()
    message_string = "a"*1001
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    with pytest.raises(InputError):
        message_send_v2(user_token, channel_id, message_string)

def test_sender_non_channel_member(reg_user, crt_channel, send_message):
    clear_v2()
    user_1_token = reg_user(0)['token']
    channel_id = crt_channel(user_1_token)['channel_id']
    user_2_token = reg_user(1)['token']
    with pytest.raises(AccessError):
        send_message(user_2_token, channel_id, 0)

def test_standup_start(reg_user, crt_channel, standup_message):
    clear_v2()
    token = reg_user(0)['token']
    channel_id = crt_channel(token)['channel_id']
    
    standup_message(token, channel_id)

    assert standup_active_v1(token, channel_id)['is_active']

def test_invalid_token(reg_user, crt_channel, send_message):
    clear_v2()
    user_token = reg_user(0)['token']
    channel_id = crt_channel(user_token)['channel_id']
    with pytest.raises(AccessError):
        send_message("Invalid token", channel_id, 0)