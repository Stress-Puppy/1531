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
def InputError():
    return 400

@pytest.fixture
def AccessError():
    return 403

# InputError when any of:
      
#         Channel ID is not a valid channel
#         When user with user id u_id is already an owner of the channel
      
# AccessError when the authorised user is not an owner of the **Dreams**, or an owner of this channel

# Parameters:(token, channel_id, u_id)
# Return Type:{}

# channel_addowner_v1()
# invaile token 
def test_invalid_token(reg_user, create_channel, AccessError):
    
    clear_v2()
    new_user = reg_user(0)
    user_id =  new_user['auth_user_id']
    user_token = new_user['token']
    channel_id = create_channel(user_token)['channel_id']

    channel_addowner_request = channel_addowner_v1("invalid_token", channel_id, user_id)
    assert channel_addowner_request.status_code == AccessError


#         Channel ID is not a valid channel
def test_invalid_channel(reg_user, create_channel, InputError):

    clear_v2()
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    channel_id = create_channel(user_token)['channel_id']
    
    channel_addowner_request = channel_addowner_v1(user_token, channel_id + 1, user_id)
    assert channel_addowner_request.status_code == InputError


#         When user with user id u_id is already an owner of the channel
def test_already_owner(reg_user, create_channel, InputError):

    clear_v2()
    first_user = reg_user(0)
    second_user = reg_user(1)
    first_token = first_user['token']
    second_id =  second_user['auth_user_id']
    
    channel_id = create_channel(first_token)['channel_id']
    channel_addowner_v1(first_token, channel_id, second_id)

    channel_addowner_request = channel_addowner_v1(first_token, channel_id, second_id)
    assert channel_addowner_request.status_code == InputError

#         when the authorised user is not an owner of the **Dreams**, or an owner of this channel
def test_sender_non_channel_member(reg_user, create_channel, AccessError):

    clear_v2()

    # first user is the owner of the **Dreams** as well as the owner of this channel, but the second user is neither of them   
    first_user = reg_user(0)
    second_user = reg_user(1)
    third_user = reg_user(2)
    
    first_id = first_user['auth_user_id']
    second_token =  second_user['token']
    third_token = third_user['token']

    channel_id = create_channel(third_token)['channel_id']

    channel_addowner_request = channel_addowner_v1(second_token, channel_id, first_id)
    assert channel_addowner_request.status_code == AccessError


