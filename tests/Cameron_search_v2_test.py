import pytest

from src.other import clear_v2, search_v2
from src.auth import auth_register_v2
from src.dm import dm_create_v1, dm_messages_v1
from src.channel import channel_messages_v2
from src.channels import channels_create_v2
from src.error import InputError, AccessError
from src.message import message_send_v2, message_senddm_v1

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

def test_search_v2_token(reg_user):
    clear_v2()
    query_str = 'x'*200
    reg_user(0)
    fake_token = 'random values r32fecaswd'
    with pytest.raises(AccessError): 
        search_v2(fake_token, query_str)

def test_search_v2_above_1000_characters(reg_user):
    clear_v2()
    query_str = 'x'*1001
    token_1 = reg_user(0)['token']
    with pytest.raises(InputError): 
        search_v2(token_1, query_str)

def test_search_v2_find_apples_dm(reg_user):
    clear_v2()
    query_str = 'apples' #find messages that have the same text as this 
    user_register1 = reg_user(0)
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(user_register1['token'], [auth_user_id_receiver])['dm_id']
    message = 'i love bananas, dont like apples'
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
    query_str = 'APPLES' #find messages that have the same text as this 
    user_register1 = reg_user(0)
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(user_register1['token'], [auth_user_id_receiver])['dm_id']
    message = 'i love bananas, dont like apples'
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
    query_str = 'apples' #find messages that have the same text as this 
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
            

