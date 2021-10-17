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
    
def test_channel_leave_v1_token(reg_user, basic_channel_name, AccessError):
    clear_v2()
    token_1 = reg_user(0)['token'] #use v2 because we want tokens as well 
    token_2 = reg_user(1)['token']
    channel_name = basic_channel_name
    fake_token = 'random values'
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    
    channel_join_v2(token_2, channel_id)
    channel_leave_request = channel_leave_v1(fake_token, channel_id)
    channel_leave_request.status_code == AccessError

def test_channel_leave_v1_non_valid_channel_id(reg_user, basic_channel_name, InputError):
    clear_v2()
    token_1 = reg_user(0)['token'] #use v2 because we want tokens as well 
    token_2 = reg_user(1)['token']
    channel_name = basic_channel_name
    fake_channel_id = 'random values sdasdsadsadsawer'
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    channel_join_v2(token_2, channel_id) #user is able to join a real channel
    
    channel_leave_request = channel_leave_v1(token_2, fake_channel_id)
    channel_leave_request.status_code == InputError#channel does not exist cant leave it 


def test_channel_leave_v1_auth_user_not_member_of_channel(reg_user, basic_channel_name, AccessError):
    clear_v2()
    token_1 = reg_user(0)['token'] #use v2 because we want tokens as well 
    token_2 = reg_user(1)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    
    channel_leave_request = channel_leave_v1(token_2, channel_id) #user never joined the channel so cant leave a channel you are not in 
    channel_leave_request.status_code == AccessError

def test_leaved_user_is_not_a_member(reg_user, basic_channel_name):
    clear_v2()
    token_1 = reg_user(0)['token'] #use v2 because we want tokens as well 
    user_register2 = reg_user(1)
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']

    channel_join_v2(user_register2['token'], channel_id)
    channel_details = channel_details_v2(token_1, channel_id)
    check_joined = False
    for members in channel_details['all_members']:
        if user_register2['auth_user_id'] == members['u_id']: # Verify that joined user is apart of the channel
            check_joined = True
    assert check_joined == True
    channel_leave_v1(user_register2['token'], channel_id)
    channel_details = channel_details_v2(token_1, channel_id) #this was the issue its in the wrong order
    for members in channel_details['all_members']:
        assert user_register2['auth_user_id'] != members['u_id']# making sure this user had really left the channel

def test_channel_owner_leave(reg_user, basic_channel_name):
    clear_v2()
    user_1 = reg_user(0)
    token_1 = user_1['token']
    id_1 = user_1['auth_user_id']
    token_2 = reg_user(1)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    channel_join_v2(token_2, channel_id)

    channel_leave_v1(token_1, channel_id)
    channel_details = channel_details_v2(token_2, channel_id)
    assert id_1 not in channel_details['all_members'] # Verify that owner has left channel
    assert id_1 not in channel_details['owner_members']
