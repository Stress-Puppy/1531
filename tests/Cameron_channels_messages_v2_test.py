import pytest

from src.other import clear_v2
from src.auth import auth_register_v2
from src.error import InputError, AccessError
from src.channels import channels_create_v2
from src.message import message_send_v2
from src.channel import channel_messages_v2

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def basic_channel_name(): 
    return 'test_name'

def test_channel_messages_v2_token(reg_user, basic_channel_name): 
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    start = 0
    fake_token = 'random values r32fecaswd'
    with pytest.raises(AccessError): 
        channel_messages_v2(fake_token, channel_id, start)

def test_single_message(reg_user, basic_channel_name):
    clear_v2()
    user_1 = reg_user(0)
    token_1 = user_1['token']
    id_1 = user_1['auth_user_id']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    start = 0
    message = "Test"
    message_id = message_send_v2(token_1, channel_id, message)['message_id']
    messages = channel_messages_v2(token_1, channel_id, start)
    assert len(messages['messages']) == 1 # Should only be one message
    assert messages['start'] == start
    assert messages['end'] == -1
    message_details = messages['messages'][0]
    assert message_details['message_id'] == message_id
    assert message_details['u_id'] == id_1
    assert message_details['message'] == message

def test_50_messages(reg_user, basic_channel_name):
    clear_v2()
    user_1 = reg_user(0)
    token_1 = user_1['token']
    id_1 = user_1['auth_user_id']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    message_count = 50
    message_ids = []
    for i in range(message_count):
        message = f"Test{i}"
        message_id = message_send_v2(token_1, channel_id, message)['message_id']
        message_ids.append(message_id)
    start = 0
    message_dict = channel_messages_v2(token_1, channel_id, start)
    messages = message_dict['messages']
    messages.reverse() # Most recent message should now be last
    # Reverse for purpose of comparison
    assert len(messages) == message_count
    assert message_dict['start'] == start
    assert message_dict['end'] == -1
    for i in range(message_count):
        message_details = messages[i]
        assert message_details['message_id'] == message_ids[i]
        assert message_details['u_id'] == id_1
        assert message_details['message'] == f"Test{i}"

def test_more_than_50_messages(reg_user, basic_channel_name):
    clear_v2()
    user_1 = reg_user(0)
    token_1 = user_1['token']
    id_1 = user_1['auth_user_id']
    channel_name = basic_channel_name
    channel_id = channels_create_v2(token_1, channel_name, True)['channel_id']
    message_count = 51
    message_ids = []
    for i in range(message_count):
        message = f"Test{i}"
        message_id = message_send_v2(token_1, channel_id, message)['message_id']
        message_ids.append(message_id)
    start = 0
    message_dict = channel_messages_v2(token_1, channel_id, start)
    messages = message_dict['messages']
    messages.reverse() # Most recent message should now be last
    # Reverse for purpose of comparison
    assert len(messages) == message_count - 1
    assert message_dict['start'] == start
    assert message_dict['end'] == 50
    for i in range(len(messages)):
        message_details = messages[i]
        assert message_details['message_id'] == message_ids[i+1]
        assert message_details['u_id'] == id_1
        assert message_details['message'] == f"Test{i+1}"

def test_channel_messages_v2_channel_id_not_valid(reg_user): 
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_id = -1 #'garbage values' 
    start = 0
    with pytest.raises(InputError):
        channel_messages_v2(token_1, channel_id, start) #this should not work as channel is not valid

def test_channel_messages_v2_channel_id_not_valid_non_negative(reg_user): 
    clear_v2()
    token_1 = reg_user(0)['token']
    channel_id = 'garbage values' 
    start = 0
    with pytest.raises(InputError):
        channel_messages_v2(token_1, channel_id, start) #this should not work as channel is not valid
        
        
def test_channel_messages_v2_start_greater_than_total(reg_user, basic_channel_name): 
    clear_v2()
    token_1 = reg_user(0)['token']
    name = basic_channel_name
    is_public = True
    channel_id = channels_create_v2(token_1, name, is_public)['channel_id']
    start = 200
    with pytest.raises(InputError):
        channel_messages_v2(token_1, channel_id, start) #this should not work as there is more than 50 messages which is the limit of this function


def test_channel_messages_v2_start_negative(reg_user, basic_channel_name): 
    clear_v2()
    token_1 = reg_user(0)['token']
    name = basic_channel_name
    is_public = True
    channel_id = channels_create_v2(token_1, name, is_public)['channel_id']
    start = -1
    with pytest.raises(InputError):
        channel_messages_v2(token_1, channel_id, start)

def test_channel_messages_v2_auth_user_is_not_memeber(reg_user, basic_channel_name):
    clear_v2()
    token_1 = reg_user(0)['token']
    token_2 = reg_user(1)['token']
    name = basic_channel_name 
    is_public = True
    channel_id = channels_create_v2(token_1, name, is_public)['channel_id']
    start = 0
    with pytest.raises(AccessError):
        channel_messages_v2(token_2, channel_id, start) #created 2 users as only auth_user_id_1 is in the channel, auth_user_id_2 should not be able to send messages
