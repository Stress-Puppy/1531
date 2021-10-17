import pytest

from src.standup import standup_start_v1, standup_active_v1
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.channel import channel_join_v2
from src.other import clear_v2
from src.error import InputError, AccessError
from time import sleep

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def basic_channel_name(): 
    return 'test_name'
    
def test_standup_start_v1_token(reg_user, basic_channel_name):
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    fake_token ='adadsafqwevdw3qwqaswd'
    standup_length = 1
    
    with pytest.raises(AccessError):
        standup_start_v1(fake_token, channel_id, standup_length)

def test_standup_start_v1_invalid_channel_id(reg_user, basic_channel_name):
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    standup_length = 1
    
    with pytest.raises(InputError):
        standup_start_v1(token_1, channel_id+1, standup_length) #channel id does not exist 

def test_standup_start_v1_active_standup_currently_running_in_channel(reg_user, basic_channel_name):
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    standup_length = 10 
    standup_start_v1(token_1, channel_id, standup_length)
    
    with pytest.raises(InputError):
        standup_start_v1(token_1, channel_id, standup_length)# standup already running in the channel

def test_standup_start_v1_another_user_cant_start_standup_when_standup_running(reg_user, basic_channel_name):
    clear_v2()
    token_1 = reg_user(0)['token']
    joined_user_token = reg_user(1)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    standup_length = 10
    channel_join_v2(joined_user_token, channel_id)
    standup_start_v1(token_1, channel_id, standup_length)
    
    with pytest.raises(InputError):
        standup_start_v1(joined_user_token, channel_id, standup_length) # standup already running in the channel
        
def test_standup_start_v1_auth_user_not_in_channel(reg_user, basic_channel_name):
    clear_v2()
    token_1 = reg_user(0)['token']
    user_not_in_channel_token = reg_user(1)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    standup_length = 1
    
    with pytest.raises(AccessError):
        standup_start_v1(user_not_in_channel_token, channel_id, standup_length)#user not inside the channel cant stand up

#test if can_still run standup when its being run in another channel should have no clash between channels
def test_standup_start_v1_non_clash_between_channels_with_standup(reg_user, basic_channel_name):
    clear_v2()
    token_1 = reg_user(0)['token']
    token_2 = reg_user(1)['token']
    channel_name = basic_channel_name
    channel_id_1 = channels_create_v2(token_1, channel_name, True)['channel_id']
    channel_id_2 = channels_create_v2(token_2, 'nice channel', True)['channel_id'] #second channel
    standup_length = 5
    
    standup_start_v1(token_1, channel_id_1, standup_length)
    standup_start_v1(token_2, channel_id_2, standup_length)
    
    is_active_channel_1 = standup_active_v1(token_1, channel_id_1)['is_active']
    assert is_active_channel_1 == True 
    
    is_active_channel_2 = standup_active_v1(token_2, channel_id_2)['is_active']
    assert is_active_channel_2 == True 

#test standup not started in both channels that user is apart of
def test_standup_start_v1_standup_not_started_in_multiple_channels_with_same_user(reg_user, basic_channel_name):
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_name = basic_channel_name
    channel_id_1 = channels_create_v2(token_1, channel_name, True)['channel_id']
    channel_id_2 = channels_create_v2(token_1, 'nice channel', True)['channel_id'] #second channel
    standup_length = 1

    standup_start_v1(token_1, channel_id_1, standup_length)
    
    is_active_channel_1 = standup_active_v1(token_1, channel_id_1)['is_active']
    assert is_active_channel_1 == True 
    
    is_active_channel_2 = standup_active_v1(token_1, channel_id_2)['is_active']
    assert is_active_channel_2 == False
    
def test_standup_start_currently_running_standup(reg_user, basic_channel_name):
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    standup_length = 10
    
    is_active = standup_active_v1(token_1, channel_id)['is_active']
    assert is_active == False
    
    standup_start_v1(token_1, channel_id, standup_length)
    
    is_active = standup_active_v1(token_1, channel_id)['is_active']
    assert is_active == True #now that standup is running this should change to True 
    
def test_standup_start_user_that_joined_channel_can_standup(reg_user, basic_channel_name):
    clear_v2()
    token_1 = reg_user(0)['token']
    joined_user_token = reg_user(1)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    standup_length = 10
    
    channel_join_v2(joined_user_token, channel_id)
    is_active = standup_active_v1(joined_user_token, channel_id)['is_active']
    assert is_active == False
    
    standup_start_v1(joined_user_token, channel_id, standup_length)
    
    is_active = standup_active_v1(joined_user_token, channel_id)['is_active']
    assert is_active == True #now that standup is running this should change to True 
