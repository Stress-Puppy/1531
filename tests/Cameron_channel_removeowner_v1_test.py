import pytest

from src.error import InputError, AccessError
from src.auth import auth_register_v2
from src.other import clear_v2
from src.channels import channels_create_v2
from src.channel import channel_addowner_v1, channel_removeowner_v1, channel_join_v2, channel_details_v2
from src.admin import admin_userpermission_change_v1

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def basic_channel_name():
    return 'test_name'


def test_channel_removeowner_v1_token(reg_user, basic_channel_name):
    clear_v2()
    channel_name = basic_channel_name
    token_1 = reg_user(0)['token']
    auth_user_id_2 = reg_user(1)['auth_user_id']
    fake_token = 'random values'
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    channel_addowner_v1(token_1, channel_id, auth_user_id_2) #add this user as the owner
    
    with pytest.raises(AccessError):
        channel_removeowner_v1(fake_token, channel_id, auth_user_id_2) #invalid token

def test_channel_removeowner_v1_channel_id_invalid(reg_user, basic_channel_name):
    clear_v2()
    token_1 = reg_user(0)['token']
    auth_user_id_2 = reg_user(1)['auth_user_id']
    fake_channel_id = 'random values'
    channel_id = channels_create_v2(token_1, basic_channel_name, True)['channel_id']
    channel_addowner_v1(token_1, channel_id, auth_user_id_2) #add this user as the owner
    
    with pytest.raises(InputError):
        channel_removeowner_v1(token_1, fake_channel_id, auth_user_id_2) #invalid channel_id 
    
def test_channel_removeowner_v1_user_id_not_an_owner(reg_user, basic_channel_name):
    clear_v2()
    channel_name = basic_channel_name
    token_1 = reg_user(0)['token']
    auth_user_id_2 = reg_user(1)['auth_user_id']
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    #join 
    with pytest.raises(InputError):
        channel_removeowner_v1(token_1, channel_id, auth_user_id_2) #this user is not an owner of the channel

def test_channel_removeowner_v1_only_owner_in_channel(reg_user, basic_channel_name):
    clear_v2()
    channel_name = basic_channel_name
    basic_user = reg_user(0)
    channel_id = channels_create_v2(basic_user['token'], channel_name, True)['channel_id']
    
    with pytest.raises(InputError):
        channel_removeowner_v1(basic_user['token'], channel_id, basic_user['auth_user_id']) #this is the only owner of the channel cant remove the only owner

def test_remove_owner(reg_user, basic_channel_name):
    clear_v2()
    owner_user = reg_user(0)
    basic_user =reg_user(1)
    channel_id = channels_create_v2(owner_user['token'], basic_channel_name, True)['channel_id']
    channel_addowner_v1(owner_user['token'], channel_id, basic_user['auth_user_id'])
    channel_removeowner_v1(basic_user['token'], channel_id, owner_user['auth_user_id'])
    channel_owners = channel_details_v2(basic_user['token'], channel_id)['owner_members']
    owner_ids = [owner['u_id'] for owner in channel_owners]
    assert owner_user['auth_user_id'] not in owner_ids # Check that owner has been removed


def test_channel_removeowner_v1_auth_user_not_owner_of_channel(reg_user, basic_channel_name):
    clear_v2()
    channel_name = basic_channel_name
    token_1 = reg_user(0)['token']
    user_register2 = reg_user(1)
    user_register3 = reg_user(2)
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    #join
    channel_join_v2(user_register2['token'], channel_id)
    channel_join_v2(user_register3['token'], channel_id)
    channel_addowner_v1(token_1, channel_id, user_register3['auth_user_id'])
    #user 2 cant remove user 3 // promote user 3 to owner
    with pytest.raises(AccessError):
        channel_removeowner_v1(user_register2['token'], channel_id, user_register3['auth_user_id']) #a normal member of the channel cant remove a owner of the channel
