import pytest

from src.other import clear_v2
from src.auth import auth_register_v2
from src.dm import dm_create_v1, dm_list_v1, dm_details_v1, dm_messages_v1
from src.error import InputError, AccessError
from src.message import message_senddm_v1

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def basic_message():
    return 'send us $2000 paypal its ya boi'

def test_dm_message_senddm_v1_token(reg_user, basic_message): 
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    fake_token = 'garbage values' 
    message = basic_message
    with pytest.raises(AccessError):
        message_senddm_v1(fake_token, dm_id, message) #check token

def test_dm_message_senddm_v1_message_more_than_1000_characters(reg_user): 
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    yuge_string = 'a'*1001 #check 1000 and 1001
    
    with pytest.raises(InputError):
        message_senddm_v1(token_sender, dm_id, yuge_string) #yuge strings over 1000 characters so will raise error

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

def test_dm_message_senddm_v1_auth_user_not_member(reg_user, basic_message):
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    non_member_of_dm_token = reg_user(2)['token']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    message = basic_message
    with pytest.raises(AccessError):
        message_senddm_v1(non_member_of_dm_token, dm_id, message) #cant post when the user is not part of the dm 
    
def test_dm_message_senddm_v1_no_valid_dm_id_found(reg_user, basic_message):
    clear_v2()
    token_sender = reg_user(0)['token']
    dm_id = 'random values asf3q2vdvdsan cjewqjfqpfd'
    message = basic_message
    with pytest.raises(InputError):
        message_senddm_v1(token_sender, dm_id, message) #invalid dm_id so cant sent a message this will fail 

