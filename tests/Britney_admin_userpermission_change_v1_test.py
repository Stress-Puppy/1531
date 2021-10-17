import pytest

from src.admin import admin_userpermission_change_v1
from src.channel import channel_join_v2, channel_details_v2
from src.channels import channels_create_v2
from src.auth import auth_register_v2
from src.other import clear_v2
from src.error import InputError, AccessError

# InputError when any of:
      
#         u_id does not refer to a valid user
#         permission_id does not refer to a value permission
      
# AccessError when
      
#         The authorised user is not an owner

# Parameters:(token, u_id, permission_id)
# Return Type:{}

# admin_userpermission_change_v1()


@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def crt_channel():
    def _create_channel(token, is_public):
        return channels_create_v2(token, 'channel_1', is_public)
    return _create_channel

#         auth_user_id does not refer to a valid user
def test_invalid_user_id(reg_user):
    
    clear_v2()
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id = new_user['auth_user_id']
    permission_id = 1
    
    with pytest.raises(InputError):
        admin_userpermission_change_v1(user_token, user_id + 1, permission_id)


#         permission_id does not refer to a value permission
def test_invalue_permission(reg_user):
    clear_v2()
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id = new_user['auth_user_id']
    permission_id = 5

    with pytest.raises(InputError):
        admin_userpermission_change_v1(user_token, user_id, permission_id)

#         The authorised user is not an owner
def test_auth_user_is_not_owner(reg_user):
    clear_v2()
    reg_user(0)
    second_user = reg_user(1)
    third_user = reg_user(2)
    
    third_token = third_user['token']
    second_id = second_user['auth_user_id']
    permission_id = 1

    with pytest.raises(AccessError):
        admin_userpermission_change_v1(third_token, second_id, permission_id)

def test_change_basic_user_to_dreams_owner(reg_user, crt_channel):
    clear_v2()
    first_user_token = reg_user(0)['token']

    second_user = reg_user(1)
    second_token = second_user['token']
    second_id = second_user['auth_user_id']

    permission_id = 1
    admin_userpermission_change_v1(first_user_token, second_id, permission_id) # Make second user owner
    channel_id = crt_channel(first_user_token, False)['channel_id']
    channel_join_v2(second_token, channel_id) # Dreams owner can join private channel
    channel_members = channel_details_v2(second_token, channel_id)['all_members']
    member_ids = [member['u_id'] for member in channel_members]
    assert second_id in member_ids

def test_change_dreams_owner_to_basic_user(reg_user, crt_channel):
    clear_v2()
    first_user = reg_user(0)
    first_token = first_user['token']
    first_id = first_user['auth_user_id']

    second_user = reg_user(1)
    second_token = second_user['token']
    second_id = second_user['auth_user_id']

    permission_id_1 = 1
    admin_userpermission_change_v1(first_token, second_id, permission_id_1) # Make second user owner
    permission_id_2 = 2
    admin_userpermission_change_v1(second_token, first_id, permission_id_2) # Make first user basic user
    channel_id = crt_channel(second_token, False)['channel_id']
    with pytest.raises(AccessError):
        channel_join_v2(first_token, channel_id) # Basic user can't join private channel

# invaile token 
def test_invalid_token(reg_user):
    
    clear_v2()
    new_user = reg_user(0)
    user_id = new_user['auth_user_id']
    permission_id = 1

    with pytest.raises(AccessError):
        admin_userpermission_change_v1("invalid_token", user_id, permission_id)


