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

def test_channel_create_v2_token(reg_user, basic_channel_name, AccessError): 
    clear_v2()
    reg_user(0)['token']
    channel_name = basic_channel_name
    fake_token = 'random values r32fecaswd'
    channels_create_request = channels_create_v2(fake_token, channel_name, True)
    assert channels_create_request.status_code == AccessError

def test_channel_create_v2_basic(reg_user, basic_channel_name): # test if it works
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_name = basic_channel_name
    is_public = True
    channel_id = channels_create_v2(token_1, channel_name, is_public)['channel_id']
    channelList = channels_list_v2(token_1)['channels']
    channel_id_found = False
    for channel in channelList:
        if channel_id == channel['channel_id']:
            channel_id_found = True
    #auth_user_id, channel_id = create_user_and_channel(channel_name, is_public)
    assert channel_id_found
    details = channel_details_v2(token_1, channel_id)
    assert details['name'] == channel_name
    assert len(details['owner_members']) == 1
    assert len(details['all_members']) == 1
    assert details['is_public'] == True

def test_channel_create_v2_name_greater_than_twenty_characters(reg_user, InputError):
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_name = 'Rip memeber crying room 10000000000000 and there was 3'
    is_public = True
    channels_create_request = channels_create_v2(token_1, channel_name, is_public)
    assert channels_create_request.status_code == InputError # should not work as channel ....
# name .....is more than 20 characters

def test_channel_create_v2_public_False(reg_user, basic_channel_name, AccessError):
    clear_v2()
    token_1 = reg_user(0)['token']
    token_2 = reg_user(1)['token']
    channel_name = basic_channel_name
    is_public = False
    #auth_user_id, channel_id = create_user_and_channel(channel_name, is_public)
    channel_id = channels_create_v2(token_1, channel_name, is_public)['channel_id']
    channels_create_request = channel_join_v2(token_2, channel_id)
    assert channels_create_request.status_code == AccessError # should not be able to join a private ....
#....channel without being invited


def test_channel_create_public_True_than_False(reg_user, basic_channel_name, AccessError):
    clear_v2()
    token_1 = reg_user(0)['token']
    token_2 = reg_user(1)['token']
    channel_name = basic_channel_name
    is_public = True
    channel_id = channels_create_v2(token_1, channel_name, is_public)['channel_id']
    channel_join_v2(token_2, channel_id) # this should work as the channel is ....
# ... public but should not work anymore if i set it to private

    De_name = 'private room'
    is_public_N2 = False
    channel_id_2 = channels_create_v2(token_1, De_name, is_public_N2)['channel_id']
    channels_create_request = channel_join_v2(token_2, channel_id_2)
    assert channels_create_request.status_code == AccessError
# this should test that there is nothing wrong with channels_join as the user was able to join.....
#... the other channel. Perpose of this tests is to see if the is_public is working correctly, as if it is, the user....
#...should not be able to join this channel as this was the only factor changed (made public to private)

