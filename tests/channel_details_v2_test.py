import pytest

from src.other import clear_v2
from src.auth import auth_register_v2
from src.channel import channel_details_v2, channel_join_v2
from src.channels import channels_create_v2
from src.error import InputError, AccessError
from src.config import url

@pytest.fixture
def user_details():
    def _user_details(num):
        return {'u_id' : num,
        		'email' : f"example{num}@email.com", 
		        'name_first' : f"firstname{num}", 
		        'name_last' : f"lastname{num}", 
		        'handle_str' : f"firstname{num}lastname{num}",
                'profile_img_url' : url + 'static/profile_photos/default.jpg'}
    return _user_details

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

@pytest.fixture
def ch_name():
    return 'channel_1'

def test_valid_input_public(reg_user, crt_channel, ch_name, user_details): # Test basic functionality with channel creator as only member of public channel
	clear_v2()
	user_token = reg_user(0)['token']
	channel_id = crt_channel(user_token, True)['channel_id']
	ch_details = channel_details_v2(user_token, channel_id)
	assert ch_details['name'] == ch_name
	assert ch_details['is_public'] == True
	assert len(ch_details['owner_members']) == 1
	assert len(ch_details['all_members']) == 1
	assert ch_details['owner_members'][0] == user_details(0)
	assert ch_details['all_members'][0] == user_details(0)

def test_valid_input_multi_user_public(reg_user, crt_channel, ch_name, user_details): # Test with channel creator and newly joined user as members
	clear_v2()
	auth_user_token = reg_user(0)['token']
	channel_id = crt_channel(auth_user_token, True)['channel_id']
	basic_user_token = reg_user(1)['token']
	channel_join_v2(basic_user_token, channel_id)
	ch_details = channel_details_v2(auth_user_token, channel_id)
	assert ch_details['name'] == ch_name
	assert ch_details['is_public'] == True
	assert len(ch_details['owner_members']) == 1
	assert len(ch_details['all_members']) == 2
	assert ch_details['owner_members'][0] == user_details(0)
	assert ch_details['all_members'][0] == user_details(0)
	assert ch_details['all_members'][1] == user_details(1)

def test_valid_input_private_channel(reg_user, crt_channel, ch_name, user_details): # Test obtaining details from private channel
	clear_v2()
	user_token = reg_user(0)['token']
	channel_id = crt_channel(user_token, False)['channel_id']
	ch_details = channel_details_v2(user_token, channel_id)
	assert ch_details['name'] == ch_name
	assert ch_details['is_public'] == False
	assert len(ch_details['owner_members']) == 1
	assert len(ch_details['all_members']) == 1
	assert ch_details['owner_members'][0] == user_details(0)
	assert ch_details['all_members'][0] == user_details(0)

def test_negative_channel_id(reg_user, crt_channel): # Give invalid channel id
	clear_v2()
	user_token = reg_user(0)['token']
	with pytest.raises(InputError): # Test negative channel_id (always invalid)
		channel_details_v2(user_token, -1)

def test_non_existent_channel_id(reg_user, crt_channel): # Give invalid channel id
	clear_v2()
	user_token = reg_user(0)['token']
	channel_id = crt_channel(user_token, True)['channel_id']
	with pytest.raises(InputError):
		channel_details_v2(user_token, channel_id+1)

def test_non_member_user(reg_user, crt_channel): # Give user id that is not in the channel's list of members
	clear_v2()
	user_token = reg_user(0)['token']
	channel_id = crt_channel(user_token, True)['channel_id']
	non_member_token = reg_user(1)['token']
	with pytest.raises(AccessError): # Test non-member user
		channel_details_v2(non_member_token, channel_id)

def test_invalid_token(reg_user, crt_channel): # Give invalid token
	clear_v2()
	user_token = reg_user(0)['token']
	channel_id = crt_channel(user_token, True)['channel_id']
	with pytest.raises(AccessError): # Test invalid token
		channel_details_v2("Invalid token", channel_id)
	