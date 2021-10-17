import pytest

from http_tests.route_wrappers_test import *

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def create_channel():
    def _create_channel(token):
        return channels_create_v2(token, 'channel_1', True)
    return _create_channel

@pytest.fixture
def crt_dm():
    def _create_dm(token, u_id):
        return dm_create_v1(token, u_id)
    return _create_dm


@pytest.fixture
def InputError():
    return 400

@pytest.fixture
def AccessError():
    return 403

# AccessError when: 
# the authorised user has not joined the channel or DM they are trying to share the message to

# Parameters:(token, og_message_id, message, channel_id, dm_id)
# Return Type:{shared_message_id}

# message_share_v1()

# og_message_id is the original message. channel_id is the channel that the message is being shared to, 
# and is -1 if it is being sent to a DM. dm_id is the DM that the message is being shared to, and is -1 if it is being sent to a channel.
#     message is the optional message in addition to the shared message


#  the authorised user has not joined the channel or DM they are trying to share the message to
def test_no_dm_channel(reg_user, create_channel, AccessError):

    clear_v2()
    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new dm
    new_dm = dm_create_v1(user_token, [user_id])
    dm_id = new_dm['dm_id']
    message = "Hello World !"
    # new message
    og_message_id = message_send_v2(user_token, channel_id, message)['message_id']

    another_user = auth_register_v2("britney@league.com", "goodpass123", "Stress", "Puppy")
    another_token = another_user['token']
    
    message_share_request = message_share_v1(another_token, og_message_id, message, channel_id, dm_id)
    assert message_share_request.status_code == AccessError


def test_non_dm_member(reg_user, create_channel, AccessError):
    clear_v2()
    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    new_user_2 = reg_user(1)
    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new dm
    new_dm = dm_create_v1(user_token, [user_id])
    dm_id = new_dm['dm_id']
    
    # new message
    og_message_text = 'Hi !'
    og_message_id = message_send_v2(user_token, channel_id, og_message_text)['message_id']
    
    shared_message_text = "Hello World !"
    message_share_request = message_share_v1(new_user_2['token'], og_message_id, shared_message_text, -1, dm_id)
    assert message_share_request.status_code == AccessError
  

#  common case
def test_common_case(reg_user, create_channel):

    clear_v2()
    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new dm
    new_dm = dm_create_v1(user_token, [user_id])
    dm_id = new_dm['dm_id']
    
    # new message
    og_message_text = 'Hi !'
    og_message_id = message_send_v2(user_token, channel_id, og_message_text)['message_id']
    
    shared_message_text = "Hello World !"

    shared_message_id = message_share_v1(user_token, og_message_id, shared_message_text, channel_id, dm_id)['shared_message_id']
    
    channel_messages = channel_messages_v2(user_token, channel_id, 0)['messages']
    for msg in channel_messages:
        if msg['message_id'] == shared_message_id:
            assert msg['message'] == f'{shared_message_text}\n\n{og_message_text}'

def test_common_case_dm(reg_user, crt_dm):

    clear_v2()
    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    new_user_2 = reg_user(1)
    # new channel
    dm_id = crt_dm(user_token, [new_user_2['auth_user_id']])['dm_id']
    # new dm
    new_dm = crt_dm(user_token, [new_user_2['auth_user_id']])
    new_dm_id = new_dm['dm_id']
    
    # new message
    og_message_text = 'Hi !'
    og_message_id = message_senddm_v1(user_token, dm_id, og_message_text)['message_id']
    
    shared_message_text = "Hello World !"

    shared_message_id = message_share_v1(user_token, og_message_id, shared_message_text, -1, new_dm_id)['shared_message_id']
    
    messages = dm_messages_v1(user_token, new_dm_id, 0)['messages']
    for msg in messages:
        if msg['message_id'] == shared_message_id:
            assert msg['message'] == f'{shared_message_text}\n\n{og_message_text}'

# invaile token
def test_invalid_token(reg_user, create_channel, AccessError):
    
    clear_v2()
    message = "Hello World!"
    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new dm
    new_dm = dm_create_v1(user_token, [user_id])
    dm_id = new_dm['dm_id']
    # new message
    og_message_id = message_send_v2(user_token, channel_id, message)

    message_share_request = message_share_v1("invalid_token", og_message_id, message, channel_id, dm_id)
    assert message_share_request.status_code == AccessError

  

