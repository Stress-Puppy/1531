import pytest

from http_tests.route_wrappers_test import *

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def basic_channel_name():
    return 'test_name'

@pytest.fixture
def InputError():
    return 400

@pytest.fixture
def AccessError():
    return 403


def test_channel_invite_v2_token(reg_user, basic_channel_name, AccessError): 
    clear_v2()
    token_1 = reg_user(0)['token']
    u_id = reg_user(1)['auth_user_id']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    fake_token = 'random values r32fecaswd'
    invite_request = channel_invite_v2(fake_token, channel_id, u_id)
    assert invite_request.status_code == AccessError
        

def test_channel_invite_v2_basic(reg_user, basic_channel_name): #check if channel_invite works 
    clear_v2()
    token_1 = reg_user(0)['token']  # this maker of the channel
    u_id = reg_user(1)['auth_user_id'] # this is the invitee of the channel 
    channel_name = basic_channel_name 
    is_public = False
    channel_id = channels_create_v2(token_1, channel_name, is_public)['channel_id']
    channel_invite_v2(token_1, channel_id, u_id)
    details = channel_details_v2(token_1, channel_id)
    user_found = False
    for user in details['all_members']:
        if u_id == user['u_id']:
            user_found = True
    assert user_found

#check if Dreams owner invited to channel is automatically a channel owner
def test_channel_invite_v2_dreams_owner(reg_user, basic_channel_name):
    clear_v2()
    user_1 = reg_user(0)
    u_id = user_1['auth_user_id'] # this is the invitee of the channel 
    token_1 = user_1['token']
    token_2 = reg_user(1)['token'] # this maker of the channel
    channel_name = basic_channel_name 
    is_public = False
    channel_id = channels_create_v2(token_2, channel_name, is_public)['channel_id']
    channel_invite_v2(token_2, channel_id, u_id)
    details = channel_details_v2(token_1, channel_id) #changed token_1 from u_id second user
    user_found = False
    for user in details['owner_members']:
        if u_id == user['u_id']:
            user_found = True
    assert user_found

def test_channel_invite_v2_channel_not_exist(reg_user, InputError): 
    clear_v2()
    token_1 = reg_user(0)['token']  # this maker of the channel
    u_id = reg_user(1)['auth_user_id'] # this is the invitee of the channel 
    channel_id = -1
    invite_request = channel_invite_v2(token_1, channel_id, u_id)
    assert invite_request.status_code == InputError
    
    
def test_channel_invite_v2_channel_not_exist_non_negative(reg_user, InputError):
    clear_v2()
    token_1 = reg_user(0)['token']  # this maker of the channel
    u_id = reg_user(1)['auth_user_id'] # this is the invitee of the channel
    channel_id = 'garbage values' 
    invite_request = channel_invite_v2(token_1, channel_id, u_id)
    assert invite_request.status_code == InputError # channel_id does not exist

def test_channel_invite_v2_u_id_not_valid_user(reg_user, basic_channel_name, InputError): 
    clear_v2()
    token_1 = reg_user(0)['token']  # this maker of the channel
    u_id = -1 # this is the invitee of the channel
    channel_name = basic_channel_name
    is_public = False
    channel_id = channels_create_v2(token_1, channel_name, is_public)['channel_id']
    invite_request = channel_invite_v2(token_1, channel_id, u_id)
    assert invite_request.status_code == InputError

def test_channel_invite_v2_u_id_not_valid_user_non_negative(reg_user, basic_channel_name, InputError): 
    clear_v2()
    token_1 = reg_user(0)['token']  # this maker of the channel
    u_id = 'what ever'
    name = basic_channel_name
    is_public = False
    channel_id = channels_create_v2(token_1, name, is_public)['channel_id']
    #auth_user_id, channel_id = create_user_and_channel(channel_name, is_public)
    invite_request = channel_invite_v2(token_1, channel_id, u_id)
    assert invite_request.status_code == InputError

def test_channel_invite_v2_u_id_currently_in_channel(reg_user, basic_channel_name, AccessError):
    clear_v2()
    token_1 = reg_user(0)['token']  # this maker of the channel
    new_user = reg_user(1) # this is the invitee of the channel
    channel_name = basic_channel_name
    is_public = True 
    channel_id = channels_create_v2(token_1, channel_name, is_public)['channel_id']
    #auth_user_id, channel_id = create_user_and_channel(channel_name, is_public)
    channel_join_v2(new_user['token'], channel_id) # invitee has joined channel
    invite_request = channel_invite_v2(token_1, channel_id, new_user['auth_user_id']) # the u_id is already inside 'all_members'does not need to be invited 
    assert invite_request.status_code == AccessError

def test_channel_invite_v2_authorised_user_is_not_part_of_channel(reg_user, basic_channel_name, AccessError):
    clear_v2()
    token_1 = reg_user(0)['token']  # this maker of the channel
    token_2 = reg_user(1)['token'] #user not inside channel
    u_id_3 = reg_user(2)['auth_user_id'] # this is the invitee of the channel 
    channel_name = basic_channel_name 
    is_public = False 
    channel_id = channels_create_v2(token_1, channel_name, is_public)['channel_id']
    invite_request = channel_invite_v2(token_2, channel_id, u_id_3) # this user is not part of the channel therefor they should not be able to invite another user
    assert invite_request.status_code == AccessError

