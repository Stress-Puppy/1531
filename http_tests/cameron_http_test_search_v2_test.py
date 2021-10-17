import pytest

from http_tests.route_wrappers_test import *

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def InputError():
    return 400

@pytest.fixture
def AccessError():
    return 403
    
def test_search_v2_token(reg_user, AccessError):
    clear_v2()
    query_str = 'x'*200
    reg_user(0)
    fake_token = 'random values r32fecaswd'
    search_request = search_v2(fake_token, query_str)
    assert search_request.status_code == AccessError

def test_search_v2_above_1000_characters(reg_user, InputError):
    clear_v2()
    query_str = 'x'*1001
    token_1 = reg_user(0)['token']
    search_request = search_v2(token_1, query_str)
    assert search_request.status_code == InputError

def test_search_v2_find_apples_dm(reg_user):
    clear_v2()
    query_str = 'apples'
    user_register1 = reg_user(0)
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(user_register1['token'], [auth_user_id_receiver])['dm_id']
    message = 'i love bananas, dont like apples'
    #message_senddm_v1(user_register1['token'], dm_id, message)
    message_2 = 'i love bananas'
    for _ in range(0, 20): 
       message_senddm_v1(user_register1['token'], dm_id, message_2)
       message_senddm_v1(user_register1['token'], dm_id, message)
    messages = search_v2(user_register1['token'], query_str)['messages']
    for single_message in messages: 
        assert single_message['message'] != message_2
        assert single_message['message'] == message
        
def test_search_v2_non_case_sensitive_dm(reg_user):
    clear_v2()
    query_str = 'APPLES'
    user_register1 = reg_user(0)
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(user_register1['token'], [auth_user_id_receiver])['dm_id']
    message = 'i love bananas, dont like apples'
    #message_senddm_v1(user_register1['token'], dm_id, message)
    message_2 = 'i love bananas'
    for _ in range(0, 20):
       message_senddm_v1(user_register1['token'], dm_id, message_2)
       message_senddm_v1(user_register1['token'], dm_id, message)
    messages = search_v2(user_register1['token'], query_str)['messages']
    for single_message in messages: 
        assert single_message['message'] != message_2
        assert single_message['message'] == message
        
def test_search_v2_find_apples_channel(reg_user):
    clear_v2()
    query_str = 'apples'
    user_register1 = reg_user(0)
    channel_id = channels_create_v2(user_register1['token'], 'nice channel', True)['channel_id']
    message = 'i love bananas, dont like apples'
    message_2 = 'i love bananas'
    for _ in range(0, 20): 
       message_send_v2(user_register1['token'], channel_id, message_2)
       message_send_v2(user_register1['token'], channel_id, message)
    messages = search_v2(user_register1['token'], query_str)['messages']
    for single_message in messages: 
        assert single_message['message'] != message_2
        assert single_message['message'] == message
            

'''
asumptions dm_message_no valid dm 
dm_name is == return name of details 

numbers negative numbers over 1000 characters 

what constiutus as qr string is just text"just the text"
search/v2
e.g. with qry sting apple return all messages with apple in them 
non case sentive where APPLE will work if qr string is apple
'''

