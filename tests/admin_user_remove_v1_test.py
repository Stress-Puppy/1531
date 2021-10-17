import pytest

from src.admin import admin_user_remove_v1
from src.auth import auth_register_v2, auth_login_v2
from src.channel import channel_join_v2, channel_messages_v2, channel_details_v2
from src.channels import channels_create_v2
from src.message import message_send_v2
from src.dm import dm_create_v1, dm_details_v1
from src.user import user_profile_v2
from src.other import clear_v2
from src.error import InputError, AccessError

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def crt_channel():
    def _create_channel(token):
        return channels_create_v2(token, 'channel_1', True)
    return _create_channel

@pytest.fixture
def removed_names():
    return { 'name_first' : 'Removed', 'name_last' : 'user' }

@pytest.fixture
def removed_string():
    return 'Removed user'

@pytest.fixture
def user_details():
    def _user_details(num):
        return (f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _user_details

def test_remove_user(reg_user, crt_channel, removed_names):
    clear_v2()
    admin = reg_user(0)
    basic_user_id = reg_user(1)['auth_user_id']
    profile_pre_remove = user_profile_v2(admin['token'], basic_user_id)['user']
    admin_user_remove_v1(admin['token'], basic_user_id)
    profile_post_remove = user_profile_v2(admin['token'], basic_user_id)['user']
    assert profile_post_remove['u_id'] == profile_pre_remove['u_id']
    assert profile_post_remove['email'] == profile_pre_remove['email']
    assert profile_post_remove['name_first'] == removed_names['name_first']
    assert profile_post_remove['name_last'] == removed_names['name_last']
    assert profile_post_remove['handle_str'] == profile_pre_remove['handle_str']

def test_remove_user_with_message(reg_user, crt_channel, removed_string):
    clear_v2()
    admin = reg_user(0)
    basic_user = reg_user(1)
    channel_id = crt_channel(admin['token'])['channel_id']
    channel_join_v2(basic_user['token'], channel_id)
    message_id = message_send_v2(basic_user['token'], channel_id, "Test")['message_id']
    admin_user_remove_v1(admin['token'], basic_user['auth_user_id'])
    message_info = channel_messages_v2(admin['token'], channel_id, 0)['messages'][0]
    assert message_info['message_id'] == message_id
    assert message_info['u_id'] == basic_user['auth_user_id']
    assert message_info['message'] == removed_string

def test_remove_channel_owner(reg_user, crt_channel):
    clear_v2()
    admin = reg_user(0)
    basic_user = reg_user(1)
    channel_id = crt_channel(basic_user['token'])['channel_id']
    channel_join_v2(admin['token'], channel_id)
    admin_user_remove_v1(admin['token'], basic_user['auth_user_id'])
    channel_details = channel_details_v2(admin['token'], channel_id)
    all_members = [member['u_id'] for member in channel_details['all_members']]
    owner_members = [member['u_id'] for member in channel_details['owner_members']]
    assert basic_user['auth_user_id'] not in all_members
    assert basic_user['auth_user_id'] not in owner_members

def test_remove_dm_member(reg_user, crt_channel):
    clear_v2()
    admin = reg_user(0)
    basic_user = reg_user(1)
    dm_id = dm_create_v1(admin['token'], [basic_user['auth_user_id']])['dm_id']
    admin_user_remove_v1(admin['token'], basic_user['auth_user_id'])
    dm_members = dm_details_v1(admin['token'], dm_id)['members']
    dm_member_ids = [member['u_id'] for member in dm_members]
    assert basic_user['auth_user_id'] not in dm_member_ids

def test_login_after_removed(reg_user, crt_channel, user_details):
    clear_v2()
    admin = reg_user(0)
    basic_user = reg_user(1)
    email, pword, *_ = user_details(1)
    admin_user_remove_v1(admin['token'], basic_user['auth_user_id'])
    with pytest.raises(InputError):
        auth_login_v2(email, pword)

def test_invalid_u_id(reg_user):
    clear_v2()
    admin = reg_user(0)
    with pytest.raises(InputError):
        admin_user_remove_v1(admin['token'], admin['auth_user_id']+1)

def test_user_is_only_owner(reg_user):
    clear_v2()
    admin = reg_user(0)
    with pytest.raises(InputError):
        admin_user_remove_v1(admin['token'], admin['auth_user_id'])

def test_auth_user_is_not_owner(reg_user):
    clear_v2()
    admin = reg_user(0)
    basic_user = reg_user(1)
    with pytest.raises(AccessError):
        admin_user_remove_v1(basic_user['token'], admin['auth_user_id'])

def test_invalid_token(reg_user):
    clear_v2()
    reg_user(0)
    basic_user = reg_user(1)
    with pytest.raises(AccessError):
        admin_user_remove_v1("Invalid token", basic_user['auth_user_id'])