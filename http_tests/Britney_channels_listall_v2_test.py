import pytest

from http_tests.route_wrappers_test import *

@pytest.fixture
def user_details(): 
    return ('validemail@gmail.com', '123abc!@#', 'Britney', 'Song')

@pytest.fixture
def AccessError():
    return 403

# Provide a list of all channels (and their associated details)

# Parameters:(token)

# Return Type:{ channels }

# successful list all 
def test_channels_listall_v2_correct(user_details): 
    clear_v2()
    email, pwd, fName, lName = user_details
    token = auth_register_v2(email, pwd, fName, lName)['token']

    name_1 = "Stress Puppy"
    name_2 = "Sweet Britney"
    name_3 = "Small Room"

    is_public_1 = True
    is_public_2 = False
    is_public_3 = False

    channel_id_1 = channels_create_v2(token, name_1, is_public_1)['channel_id']
    channel_id_2 = channels_create_v2(token, name_2, is_public_2)['channel_id']
    channel_id_3 = channels_create_v2(token, name_3, is_public_3)['channel_id']

    assert channels_listall_v2(token) == { 'channels' : [{'channel_id' : channel_id_1, 'name' : name_1}, 
                                                         {'channel_id' : channel_id_2, 'name' : name_2}, 
                                                         {'channel_id' : channel_id_3, 'name' : name_3}] }
    #   "channels" structure: channels = {1: {name' : 'channel_1 ', 'owner_members' : [1,2,3,4], 'all_members' : [1,2,3,4], 'is_private' : False, 'messages' : {1 : {}, 2 : {}}}} 

    #   Expect to work since we crated the channels

# case no this channel
def test_channels_listall_v2_no_channel(user_details): 
    clear_v2()
    email, pwd, fName, lName = user_details
    token = auth_register_v2(email, pwd, fName, lName)['token']

    assert (channels_listall_v2(token) == { 'channels' : [] })  

# invaile token 
def test_invalid_token(user_details, AccessError):
    
    clear_v2()

    channels_listall_request = channels_listall_v2("invalid_token")
    assert channels_listall_request.status_code == AccessError

