import pytest

from src.other import clear_v2
from src.channel import channel_join_v2, channel_details_v2
from src.channels import channels_create_v2
from src.auth import auth_register_v2
from src.error import InputError, AccessError

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

def test_joined_user_is_member(reg_user, crt_channel): # Give valid user_id and channel_id
	clear_v2()
	auth_user_token = reg_user(0)['token']
	channel_id = crt_channel(auth_user_token, True)['channel_id']
	joined_user = reg_user(1)
	channel_join_v2(joined_user['token'], channel_id)
	channel_details = channel_details_v2(auth_user_token, channel_id)
	joined_user_found = False
	for user in channel_details['all_members']:
		if joined_user['auth_user_id'] == user['u_id']:
			joined_user_found = True
	assert joined_user_found # Verify that joined user is in channel's all_members list

def test_join_when_already_member(reg_user, crt_channel): # Test what happens when a user attempts to join a channel they're already in (should do nothing)
	clear_v2()
	auth_user_token = reg_user(0)['token']
	channel_id = crt_channel(auth_user_token, True)['channel_id']
	joined_user = reg_user(1)
	channel_join_v2(joined_user['token'], channel_id)
	channel_join_v2(joined_user['token'], channel_id)
	channel_details = channel_details_v2(auth_user_token, channel_id)
	times_joined_user_found = 0 # Count number of times the joined user was found in the channel
	for user in channel_details['all_members']:
		if joined_user['auth_user_id'] == user['u_id']:
			times_joined_user_found += 1
	assert times_joined_user_found == 1 # Verify that joined user has only been added to channel's all_members list once

def test_non_global_owner_join_private_channel(reg_user, crt_channel): # Non-global-owner should be unable to join private channel 
	clear_v2()
	auth_user_token = reg_user(0)['token']
	channel_id = crt_channel(auth_user_token, False)['channel_id']
	joined_user_token = reg_user(1)['token']
	with pytest.raises(AccessError):
		assert channel_join_v2(joined_user_token, channel_id)

def test_global_owner_join_private_channel(reg_user, crt_channel): # Global owner should be able to join private channel
	clear_v2()
	global_owner = reg_user(0)
	auth_user_token = reg_user(1)['token']
	channel_id = crt_channel(auth_user_token, False)['channel_id']
	channel_join_v2(global_owner['token'], channel_id)
	channel_details = channel_details_v2(auth_user_token, channel_id)
	global_owner_found = False
	for user in channel_details['all_members']:
		if global_owner['auth_user_id'] == user['u_id']:
			global_owner_found = True
	assert global_owner_found # Verify that global owner user is in channel's all_members list

def test_negative_channel_id(reg_user, crt_channel): # Give invalid channel id
	clear_v2()
	auth_user_token = reg_user(0)['token']
	crt_channel(auth_user_token, True)['channel_id']
	joined_user_token = reg_user(1)['token']
	with pytest.raises(InputError): # Test negative channel_id (always invalid)
		assert channel_join_v2(joined_user_token, -1)

def test_non_existent_channel_id(reg_user, crt_channel): # Give invalid channel id
	clear_v2()
	auth_user_token = reg_user(0)['token']
	channel_id = crt_channel(auth_user_token, True)['channel_id']
	joined_user_token = reg_user(1)['token']
	with pytest.raises(InputError): # Test negative channel_id (always invalid)
		assert channel_join_v2(joined_user_token, channel_id+1)

def test_invalid_token(reg_user, crt_channel):
	clear_v2()
	auth_user_token = reg_user(0)['token']
	channel_id = crt_channel(auth_user_token, True)['channel_id']
	reg_user(1)
	with pytest.raises(AccessError): # Test invalid token (always raises AccessError)
		assert channel_join_v2("Invalid token", channel_id)
