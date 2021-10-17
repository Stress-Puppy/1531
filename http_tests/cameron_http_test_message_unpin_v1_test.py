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
def basic_message():
    return 'send us $2000 paypal its ya boi'

@pytest.fixture
def InputError():
    return 400

@pytest.fixture
def AccessError():
    return 403

def test_message_unpin_v1_token_channel(reg_user, basic_channel_name, basic_message, AccessError): 
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    message = basic_message
    message_id = message_send_v2(token_1, channel_id, message)['message_id']
    fake_token = 'random values r32fecaswd'
    message_pin_v1(token_1, message_id)

    message_unpin_request = message_unpin_v1(fake_token, message_id)
    assert message_unpin_request.status_code == AccessError

def test_message_unpin_v1_token_dm(reg_user, basic_message, AccessError):
    clear_v2()
    token_1 = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_1, [auth_user_id_receiver])['dm_id']
    message = basic_message
    message_id = message_senddm_v1(token_1, dm_id, message)['message_id']
    fake_token = 'random values r32fecaswd'
    message_pin_v1(token_1, message_id)

    message_unpin_request = message_unpin_v1(fake_token, message_id)
    assert message_unpin_request.status_code == AccessError
    
def test_message_unpin_v1_channel_invalid_message_id(reg_user, basic_channel_name, basic_message, InputError):
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    message = basic_message
    message_id = message_send_v2(token_1, channel_id, message)['message_id']
    message_pin_v1(token_1, message_id)
    
    message_unpin_request = message_unpin_v1(token_1, message_id+1)
    assert message_unpin_request.status_code == InputError
    
def test_message_unpin_v1_dm_invalid_message_id(reg_user, basic_message, InputError):
    clear_v2()
    token_1 = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_1, [auth_user_id_receiver])['dm_id']
    message = basic_message
    message_id = message_senddm_v1(token_1, dm_id, message)['message_id']
    
    message_pin_v1(token_1, message_id)

    message_unpin_request = message_unpin_v1(token_1, message_id+1)
    assert message_unpin_request.status_code == InputError
    
def test_message_unpin_v1_channel_message_already_unpinned(reg_user, basic_channel_name, basic_message, InputError):
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    message = basic_message
    message_id = message_send_v2(token_1, channel_id, message)['message_id']
    
    message_pin_v1(token_1, message_id)
    message_unpin_v1(token_1, message_id)
    
    message_unpin_request = message_unpin_v1(token_1, message_id)# Message with ID message_id is already unpinned
    assert message_unpin_request.status_code == InputError

def test_message_unpin_v1_dm_message_already_unpinned(reg_user, basic_message, InputError):
    clear_v2()
    token_1 = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_1, [auth_user_id_receiver])['dm_id']
    message = basic_message
    message_id = message_senddm_v1(token_1, dm_id, message)['message_id']
    
    message_pin_v1(token_1, message_id)
    message_unpin_v1(token_1, message_id)
    
    message_unpin_request = message_unpin_v1(token_1, message_id)# Message with ID message_id is already unpinned
    assert message_unpin_request.status_code == InputError

def test_message_unpin_v1_auth_user_not_part_of_channel(reg_user, basic_channel_name, basic_message, AccessError):
    clear_v2()
    token_1 = reg_user(0)['token']
    non_member_of_channel_token = reg_user(1)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    message = basic_message
    message_id = message_send_v2(token_1, channel_id, message)['message_id']
    
    message_pin_v1(token_1, message_id)
    
    message_unpin_request = message_unpin_v1(non_member_of_channel_token, message_id) # The authorised user is not a member of the channel
    assert message_unpin_request.status_code == AccessError

def test_message_unpin_v1_auth_user_not_part_of_dm(reg_user, basic_message, AccessError):
    clear_v2()
    token_1 = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    non_member_of_dm_token = reg_user(2)['token']
    dm_id = dm_create_v1(token_1, [auth_user_id_receiver])['dm_id']
    message = basic_message
    message_id = message_senddm_v1(token_1, dm_id, message)['message_id']
    
    message_pin_v1(token_1, message_id)

    message_unpin_request = message_unpin_v1(non_member_of_dm_token, message_id)# The authorised user is not a member of the dm
    assert message_unpin_request.status_code == AccessError

def test_message_unpin_auth_user_is_non_owner_of_channel(reg_user, basic_channel_name, basic_message, AccessError):
    clear_v2()
    token_1 = reg_user(0)['token']
    non_owner_of_channel_token = reg_user(1)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    channel_join_v2(non_owner_of_channel_token, channel_id) #second user joinned the channel
    message = basic_message
    message_id = message_send_v2(token_1, channel_id, message)['message_id']
    
    message_pin_v1(token_1, message_id)
    
    message_unpin_request = message_unpin_v1(non_owner_of_channel_token, message_id)# The authorised user is not an owner of the channel
    assert message_unpin_request.status_code == AccessError

def test_message_unpin_auth_user_is_non_owner_of_dm(reg_user, basic_message, AccessError):
    clear_v2()
    token_1 = reg_user(0)['token']
    non_owner_of_dm = reg_user(1)
    dm_id = dm_create_v1(token_1, [non_owner_of_dm['auth_user_id']])['dm_id']
    message = basic_message
    message_id = message_senddm_v1(token_1, dm_id, message)['message_id']
    
    message_pin_v1(token_1, message_id)

    message_unpin_request = message_unpin_v1(non_owner_of_dm['token'], message_id)# The authorised user is not an owner of the dm
    assert message_unpin_request.status_code == AccessError
    
def test_message_unpin_channel_basic(reg_user, basic_channel_name, basic_message):
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    message = basic_message
    message_id = message_send_v2(token_1, channel_id, message)['message_id']
    message_pin_v1(token_1, message_id)
    start = 0
    messages = channel_messages_v2(token_1, channel_id, start)['messages']
    
    assert messages[0]['message_id'] == message_id
    assert messages[0]['is_pinned'] == True
    
    message_unpin_v1(token_1, message_id)
    messages = channel_messages_v2(token_1, channel_id, start)['messages']
    
    assert messages[0]['message_id'] == message_id
    assert messages[0]['is_pinned'] == False

#messages
#List of dictionaries, where each dictionary contains types { message_id, u_id, message, time_created, reacts, is_pinned  }

def test_message_unpin_dm_basic(reg_user, basic_message):
    clear_v2()
    token_1 = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_1, [auth_user_id_receiver])['dm_id']
    message = basic_message
    message_id = message_senddm_v1(token_1, dm_id, message)['message_id']
    message_pin_v1(token_1, message_id)
    start = 0
    messages = dm_messages_v1(token_1, dm_id, start)['messages']
    
    assert messages[0]['message_id'] == message_id
    assert messages[0]['is_pinned'] == True
    
    message_unpin_v1(token_1, message_id)
    messages = dm_messages_v1(token_1, dm_id, start)['messages']
    
    assert messages[0]['message_id'] == message_id
    assert messages[0]['is_pinned'] == False
    
