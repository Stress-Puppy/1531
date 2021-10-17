import pytest

from src.auth import auth_register_v2
from src.message import message_send_v2
from src.message import message_edit_v2
from src.message import message_remove_v1
from src.channels import channels_create_v2
from src.channel import channel_messages_v2, channel_join_v2
from src.other import clear_v2
from src.error import AccessError, InputError

# InputError when any of:
      
#         Length of message is over 1000 characters
#         message_id refers to a deleted message
      
# AccessError when none of the following are true:
      
#         Message with message_id was sent by the authorised user making this request
#         The authorised user is an owner of this channel or the **Dreams**

# Parameters:(token, message_id, message)
# Return Type:{}

# message_edit_v2()

# Given a message, update its text with new text. If the new message is an empty string, the message is deleted.

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


# invaile token 
def test_invalid_token(reg_user, create_channel):
    
    clear_v2()
    message = "Hello World!"
    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new message
    message_id = message_send_v2(user_token, channel_id, message)['message_id']

    with pytest.raises(AccessError):
        message_edit_v2("invalid_token", message_id, message)

def test_non_string_message(reg_user, create_channel):
    
    clear_v2()
    message = "Hello World!"
    # new user
    new_user = reg_user(0)
    user_token = new_user['token']
    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new message
    message_id = message_send_v2(user_token, channel_id, message)['message_id']

    with pytest.raises(InputError):
        message_edit_v2(user_token, message_id, 123923)

#  Length of message is over 1000 characters
def test_too_long(reg_user, create_channel):

    clear_v2()
    # new user
    new_user = reg_user(0)
    user_token = new_user['token']

    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new message
    message_id = message_send_v2(user_token, channel_id, "test")['message_id']
    
    message = "a"*1001

    with pytest.raises(InputError):
        message_edit_v2(user_token, message_id, message)

#  message_id refers to a deleted message
def test_delected_message(reg_user, create_channel):

    clear_v2()
    
    message = "Hello World!"
    # new user
    new_user = reg_user(0)
    user_token = new_user['token']

    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new message
    message_id = message_send_v2(user_token, channel_id, message)['message_id']
    # delected
    message_remove_v1(user_token, message_id)

    with pytest.raises(InputError):
        message_edit_v2(user_token, message_id, message)

#  when none of the following are true:
      
#         Message with message_id was sent by the authorised user making this request
#         The authorised user is an owner of this channel or the **Dreams**
def test_not_owner(reg_user, create_channel):

    clear_v2()

    message = "Hello World!"
    # new user
    new_user = reg_user(0)
    user_token = new_user['token']

    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new message
    message_id = message_send_v2(user_token, channel_id, message)['message_id']

    another_user = auth_register_v2("britney@league.com", "goodpass123", "Stress", "Puppy")
    another_token = another_user['token']
    
    with pytest.raises(AccessError):
        message_edit_v2(another_token, message_id, message)


# common successful case 1: change the message
def test_change(reg_user, create_channel):

    clear_v2()

    # new user
    new_user = reg_user(0)
    user_token = new_user['token']

    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new message
    message_id = message_send_v2(user_token, channel_id, "Hi Britney!")['message_id']
    
    message = "Hello World!"
    message_edit_v2(user_token, message_id, message)

    messages = channel_messages_v2(user_token, channel_id, 0)['messages']

    for msg in messages:
        if msg['message_id'] == message_id:
            assert msg['message'] == "Hello World!"

def test_change_non_author_non_dreams_owner_channel_owner(reg_user, create_channel):

    clear_v2()

    # new user
    reg_user(0) # Create first user, who is a dreams owner (for testing purposes, we want non-dreams-owners)
    new_user = reg_user(1)
    user_token = new_user['token']
    new_user_2 = reg_user(2)

    # new channel
    channel_id = create_channel(user_token)['channel_id']
    channel_join_v2(new_user_2['token'], channel_id)
    # new message
    message_id = message_send_v2(new_user_2['token'], channel_id, "Hi Britney!")['message_id']
    
    message = "Hello World!"
    message_edit_v2(user_token, message_id, message)

    messages = channel_messages_v2(user_token, channel_id, 0)['messages']

    for msg in messages:
        if msg['message_id'] == message_id:
            assert msg['message'] == "Hello World!"

# common successful case 2: empty message, so delete
def test_delete(reg_user, create_channel):

    clear_v2()

    message = "Hello World!"
    # new user
    new_user = reg_user(0)
    user_token = new_user['token']

    # new channel
    channel_id = create_channel(user_token)['channel_id']
    # new message
    message_id = message_send_v2(user_token, channel_id, message)['message_id']
    
    message_edit_v2(user_token, message_id, "")

    messages = channel_messages_v2(user_token, channel_id, 0)['messages']

    assert not len(messages)


