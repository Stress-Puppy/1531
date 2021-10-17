import pytest

from datetime import timezone
from datetime import datetime
from datetime import timedelta

from src.auth import auth_register_v2
from src.dm import dm_messages_v1, dm_create_v1
from src.message import message_senddm_v1, message_sendlaterdm_v1
from src.other import clear_v2
from src.error import InputError, AccessError

# InputError when any of:
      
#         DM ID is not a valid DM
#         Message is more than 1000 characters
#         Time sent is a time in the past
      
# AccessError when :
      
#         the authorised user has not joined the DM they are trying to post to

# Parameters:(token, dm_id, message, time_sent)
# Return Type:{ message_id }

# message_sendlaterdm_v1()

# Send a message from authorised_user to the DM specified by dm_id automatically at a specified time in the future

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def message_text():
    def _message_text(num):
        return f"Test message {num}."
    return _message_text

# common case
def test_common(reg_user, message_text):
    clear_v2()
    user_token = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(user_token, [auth_user_id_receiver])['dm_id']

    dt = datetime.now(timezone.utc) + timedelta(hours=0, minutes=1)  
    time_sent = dt.replace(tzinfo=timezone.utc).timestamp()

    assert message_sendlaterdm_v1(user_token, dm_id, message_text(0), time_sent)['message_id'] == 0
    prev_message_id = message_senddm_v1(user_token, dm_id, message_text(1))['message_id']
    assert message_sendlaterdm_v1(user_token, dm_id, message_text(2), time_sent)['message_id'] == prev_message_id + 1


# dm ID is not a valid dm
def test_invaild_dm(reg_user, message_text):
    clear_v2()
    user_token = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(user_token, [auth_user_id_receiver])['dm_id']
    message = message_text(0)

    dt = datetime.now(timezone.utc) + timedelta(hours=9, minutes=50)  
    time_sent = dt.replace(tzinfo=timezone.utc).timestamp()

    with pytest.raises(InputError):
        message_sendlaterdm_v1(user_token, dm_id + 1, message, time_sent)


# Message is more than 1000 characters
def test_long_message(reg_user, message_text):
    clear_v2()
    user_token = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(user_token, [auth_user_id_receiver])['dm_id']
    message = 'a' * 1001

    dt = datetime.now(timezone.utc) + timedelta(hours=9, minutes=50)  
    time_sent = dt.replace(tzinfo=timezone.utc).timestamp()

    with pytest.raises(InputError):
        message_sendlaterdm_v1(user_token, dm_id, message, time_sent)

# Time sent is a time in the past
def test_time_past(reg_user, message_text):
    clear_v2()
    user_token = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(user_token, [auth_user_id_receiver])['dm_id']
    message = message_text(0)

    dt = datetime.now(timezone.utc) - timedelta(hours=0, minutes=50) 
    time_sent = dt.replace(tzinfo=timezone.utc).timestamp()

    with pytest.raises(InputError):
        message_sendlaterdm_v1(user_token, dm_id, message, time_sent)

# the authorised user has not joined the dm they are trying to post to
def test_sender_non_dm_member(reg_user, message_text):
    clear_v2()

    user_token = reg_user(0)['token']

    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(user_token, [auth_user_id_receiver])['dm_id']
    
    user_token_1 = reg_user(2)['token']
    message = message_text(0)

    dt = datetime.now(timezone.utc) + timedelta(hours=9, minutes=50)  
    time_sent = dt.replace(tzinfo=timezone.utc).timestamp()

    with pytest.raises(AccessError):
        message_sendlaterdm_v1(user_token_1, dm_id, message, time_sent)


# invalid_token
def test_invalid_token(reg_user, message_text):
    
    clear_v2()
    user_token = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(user_token, [auth_user_id_receiver])['dm_id']
    message = message_text(0)

    dt = datetime.now(timezone.utc) + timedelta(hours=9, minutes=50)  
    time_sent = dt.replace(tzinfo=timezone.utc).timestamp()

    with pytest.raises(AccessError):
        message_sendlaterdm_v1("Invalid token", dm_id, message, time_sent)