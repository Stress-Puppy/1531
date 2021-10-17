import pytest

from src.auth import auth_register_v2
from src.message import message_share_v1, message_send_v2, message_senddm_v1, message_react_v1
from src.dm import dm_create_v1, dm_messages_v1
from src.channels import channels_create_v2
from src.channel import channel_messages_v2
from src.other import clear_v2
from src.error import AccessError, InputError


# AccessError when: 
    # The authorised user is not a member of the channel or DM that the message is within

# InputError when: 
    # message_id is not a valid message within a channel or DM that the authorised user has joined
    # react_id is not a valid React ID. The only valid react ID the frontend has is 1
    # Message with ID message_id already contains an active React with ID react_id from the authorised user

# Parameters:(token, message_id, react_id)
# Return Type:{}

# message_react_v1()

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


#  The authorised user is not a member of the channel that the message is within
def test_no_channel(reg_user, create_channel):

    clear_v2()

    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new message
    message = "Hello World !"
    message_id = message_send_v2(user_token, channel_id, message)['message_id']
    
    # anthor user
    another_user = reg_user(1)
    another_token = another_user['token']
    
    react_id = 1

    with pytest.raises(AccessError):
        message_react_v1(another_token, message_id, react_id)


#  The authorised user is not a member of the DM that the message is within
def test_no_dm(reg_user):

    clear_v2()

    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    another_user_id = reg_user(1)['auth_user_id']
    # new dm
    new_dm = dm_create_v1(user_token, [another_user_id])
    dm_id = new_dm['dm_id']
    # new message
    message = "Hello World !"
    message_id = message_senddm_v1(user_token, dm_id, message)['message_id']
    
    # anthor user
    other_user = reg_user(2)
    other_token = other_user['token']
    
    react_id = 1

    with pytest.raises(AccessError):
        message_react_v1(other_token, message_id, react_id)

# message_id is not a valid message within a DM that the authorised user has joined
def test_invaild_message_id_dm(reg_user):
    clear_v2()

    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    # new dm
    new_dm = dm_create_v1(user_token, [user_id])
    dm_id = new_dm['dm_id']
    # new message
    message = "Hello World !"
    message_id = message_senddm_v1(user_token, dm_id, message)['message_id']
    
    react_id = 1

    with pytest.raises(InputError):
        message_react_v1(user_token, message_id + 1, react_id)

# message_id is not a valid message within a channel that the authorised user has joined
def test_invaild_message_id_channel(reg_user, create_channel):
    clear_v2()

    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new message
    message = "Hello World !"
    message_id = message_send_v2(user_token, channel_id, message)['message_id']
    
    react_id = 1

    with pytest.raises(InputError):
        message_react_v1(user_token, message_id + 1, react_id)

# react_id is not a valid React ID. The only valid react ID the frontend has is 1
def test_invaild_react_id(reg_user, create_channel):
    clear_v2()

    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new message
    message = "Hello World !"
    message_id = message_send_v2(user_token, channel_id, message)['message_id']
    
    react_id = 3

    with pytest.raises(InputError):
        message_react_v1(user_token, message_id, react_id)

# Message with ID message_id already contains an active React with ID react_id from the authorised user
def test_already_react(reg_user, create_channel):
    clear_v2()

    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new message
    message = "Hello World !"
    message_id = message_send_v2(user_token, channel_id, message)['message_id']
    
    react_id = 1
    message_react_v1(user_token, message_id, react_id)
    with pytest.raises(InputError):
        message_react_v1(user_token, message_id, react_id)

# invaile token 
def test_invalid_token(reg_user, create_channel):
    
    clear_v2()
    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    # new dm
    new_dm = dm_create_v1(user_token, [user_id])
    dm_id = new_dm['dm_id']
    # new message
    message = "Hello World !"
    message_id = message_senddm_v1(user_token, dm_id, message)['message_id']
    
    react_id = 1

    with pytest.raises(AccessError):
        message_react_v1("invalid_token", message_id, react_id)

