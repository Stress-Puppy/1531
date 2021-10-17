import pytest

from http_tests.route_wrappers_test import *

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def basic_message():
    return 'send us $2000 paypal its ya boi'

@pytest.fixture
def InputError():
    return 400

@pytest.fixture
def AccessError():
    return 403
    
def test_dm_message_senddm_v1_token(reg_user, basic_message, AccessError): 
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    #messages = dm_messages_v1(token_sender, dm_id, 1)['messages']
    fake_token = 'garbage values' 
    message = basic_message
    #with pytest.raises(AccessError):
        #message_senddm_v1(fake_token, dm_id, messages['message'])
    dm_message_senddm_request = message_senddm_v1(fake_token, dm_id, message)
    assert dm_message_senddm_request.status_code == AccessError

def test_dm_message_senddm_v1_message_more_than_1000_characters(reg_user, InputError): 
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    yuge_string = 'a'*1001 #check 1000 and 1001
    
    dm_message_senddm_request = message_senddm_v1(token_sender, dm_id, yuge_string) #yuge strings over 1000 characters so will raise error
    assert dm_message_senddm_request.status_code == InputError

def test_dm_message_senddm_v1_message_exactly_1000_characters(reg_user): 
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    yuge_string = 'a'*1000
    message_id = message_senddm_v1(token_sender, dm_id, yuge_string)['message_id']
    message = dm_messages_v1(token_sender, dm_id, 0)['messages'][0]
    assert message['message_id'] == message_id
    assert message['message'] == yuge_string

def test_dm_message_senddm_v1_auth_user_not_member(reg_user, basic_message, AccessError):
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    non_member_of_dm_token = reg_user(2)['token']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    #messages = dm_messages_v1(token_sender, dm_id, 1)['messages'] # is this needed lol i can just give characters
    message = basic_message
    
    dm_message_senddm_request = message_senddm_v1(non_member_of_dm_token, dm_id, message) #cant post when the user is not part of the dm
    assert dm_message_senddm_request.status_code == AccessError
    
def test_dm_message_senddm_v1_no_valid_dm_id_found(reg_user, basic_message, InputError):
    clear_v2()
    token_sender = reg_user(0)['token']
    dm_id = 'random values asf3q2vdvdsan cjewqjfqpfd'
    #messages = dm_messages_v1(token_sender, dm_id, 1)['messages'] # is this needed lol i can just give characters// this just reads the messages alread sent yea 
    message = basic_message
    
    dm_message_senddm_request = message_senddm_v1(token_sender, dm_id, message) #invalid dm_id so cant sent a message this will fail
    assert dm_message_senddm_request.status_code == InputError


