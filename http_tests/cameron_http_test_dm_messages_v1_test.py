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

def test_dm_messages_v1_token(reg_user, AccessError): 
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    fake_token = 'garbage values' 
    start = 2
    
    dm_messages_request = dm_messages_v1(fake_token, dm_id, start)
    assert dm_messages_request.status_code == AccessError

def test_dm_messages_v1_dm_id_is_not_a_valid_dm(reg_user, InputError):
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_create_v1(token_sender, [auth_user_id_receiver])
    fake_dm_id = 9000
    start = 2
    
    dm_messages_request = dm_messages_v1(token_sender, fake_dm_id, start)
    assert dm_messages_request.status_code == InputError
    
def test_dm_messages_v1_start_is_greater_than_total(reg_user, basic_message, InputError): 
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    
    start = 57

    for _ in range(0, 55):
        message_senddm_v1(token_sender, dm_id, basic_message)
    
    dm_messages_request = dm_messages_v1(token_sender, dm_id, start) #out of bounds of the total messages in the channel
    assert dm_messages_request.status_code == InputError

def test_dm_messages_v1_auth_user_is_not_a_member_of_dm(reg_user, AccessError):
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    token_non_auth_user = reg_user(2)['token']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    start = 1
    
    dm_messages_request = dm_messages_v1(token_non_auth_user, dm_id, start) #since this user was never appart of the dm send messages
    assert dm_messages_request.status_code == AccessError
    

def test_single_message(reg_user):
    clear_v2()
    sender = reg_user(0)
    token_sender = sender['token']
    id_sender = sender['auth_user_id']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    start = 0
    message = "Test"
    message_id = message_senddm_v1(token_sender, dm_id, message)['message_id']
    messages = dm_messages_v1(token_sender, dm_id, start)
    assert len(messages['messages']) == 1 # Should only be one message
    assert messages['start'] == start
    assert messages['end'] == -1
    message_details = messages['messages'][0]
    assert message_details['message_id'] == message_id
    assert message_details['u_id'] == id_sender
    assert message_details['message'] == message

def test_start_negative(reg_user, InputError):
    clear_v2()
    sender = reg_user(0)
    token_sender = sender['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    start = -1
    message = "Test"
    message_senddm_v1(token_sender, dm_id, message)['message_id']
    
    dm_messages_request = dm_messages_v1(token_sender, dm_id, start)
    assert dm_messages_request.status_code == InputError

def test_50_messages(reg_user):
    clear_v2()
    sender = reg_user(0)
    token_sender = sender['token']
    id_sender = sender['auth_user_id']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    start = 0
    message_ids = []
    message_count = 50
    for i in range(message_count):
        message = f"Test{i}"
        message_id = message_senddm_v1(token_sender, dm_id, message)['message_id']
        message_ids.append(message_id)
    message_dict = dm_messages_v1(token_sender, dm_id, start)
    messages = message_dict['messages']
    messages.reverse() # Most recent message should now be last
    # Reverse for purpose of comparison
    assert len(messages) == message_count
    assert message_dict['start'] == start
    assert message_dict['end'] == -1
    for i in range(message_count):
        message_details = messages[i]
        assert message_details['message_id'] == message_ids[i]
        assert message_details['u_id'] == id_sender
        assert message_details['message'] == f"Test{i}"

def test_more_than_50_messages(reg_user):
    clear_v2()
    sender = reg_user(0)
    token_sender = sender['token']
    id_sender = sender['auth_user_id']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    start = 0
    message_ids = []
    message_count = 51
    for i in range(message_count):
        message = f"Test{i}"
        message_id = message_senddm_v1(token_sender, dm_id, message)['message_id']
        message_ids.append(message_id)
    message_dict = dm_messages_v1(token_sender, dm_id, start)
    messages = message_dict['messages']
    messages.reverse() # Most recent message should now be last
    # Reverse for purpose of comparison
    assert len(messages) == message_count - 1
    assert message_dict['start'] == start
    assert message_dict['end'] == 50
    for i in range(len(messages)):
        message_details = messages[i]
        assert message_details['message_id'] == message_ids[i+1]
        assert message_details['u_id'] == id_sender
        assert message_details['message'] == f"Test{i+1}"

#add basic test as well 
def test_dm_messages_v1_basics(reg_user,basic_message):
    clear_v2()
    user_register1 = reg_user(0)
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(user_register1['token'], [auth_user_id_receiver])['dm_id']
    message_id_list = []
    message = basic_message
    for _ in range(0, 20): 
        message_id = message_senddm_v1(user_register1['token'], dm_id, basic_message)['message_id'] #send 20 messages
        message_id_list.append(message_id)
    messages = dm_messages_v1(user_register1['token'], dm_id, 0)['messages'] #messages is a list of dictionaries with message_id, u_id "who sent it", and the message contained inside
    messages.reverse() # Most recent message should now be last
    # Reverse for purpose of comparison
    for single_message in messages: #inside each of our messages check if the values are correct
        assert single_message['message_id'] in message_id_list
        assert single_message['u_id'] == user_register1['auth_user_id'] #sent user is always the same for this test 
        assert single_message['message'] == message # the message is always the same for this test
    #check order for i in range() test message different, different auth user

def test_dm_messages_v1_messages_sent_in_order(reg_user,basic_message):
    clear_v2()
    user_register1 = reg_user(0)
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(user_register1['token'], [auth_user_id_receiver])['dm_id']
    message_id_list = []
    for i in range(0, 20): 
        message_id = message_senddm_v1(user_register1['token'], dm_id, basic_message)['message_id'] #send 20 messages
        message_id_list.append(message_id)
    messages = dm_messages_v1(user_register1['token'], dm_id, 0)['messages'] #messages is a list of dictionaries with message_id, u_id "who sent it", and the message contained inside
    messages.reverse() # Most recent message should now be last
    # Reverse for purpose of comparison
    for i in range(0, 20): 
        assert message_id_list[i] == messages[i]['message_id']

def test_dm_messages_v1_messages_different_message(reg_user):
    clear_v2()
    user_register1 = reg_user(0)
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id = dm_create_v1(user_register1['token'], [auth_user_id_receiver])['dm_id']
    messages_ids = []
    for i in range(0, 20): 
        message_id = message_senddm_v1(user_register1['token'], dm_id, str(i))['message_id'] #send 20 messages
        messages_ids.append(message_id)
    messages = dm_messages_v1(user_register1['token'], dm_id, 0)['messages'] #messages is a list of dictionaries with message_id, u_id "who sent it", and the message contained inside
    messages.reverse() # Most recent message should now be last
    # Reverse for purpose of comparison
    for i in range(0, 20): 
        assert messages_ids[i] == messages[i]['message_id']

