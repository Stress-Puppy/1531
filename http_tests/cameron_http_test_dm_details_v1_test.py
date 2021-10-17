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
    
def test_dm_details_v1_token(reg_user, AccessError):
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    #u_id = [auth_user_id_receiver]
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    #dm_members = [auth_user_id_sender, auth_user_id_receiver] # create a list with the ids of the users 
    fake_token = 'garbage values' 
    
    dm_details_request = dm_details_v1(fake_token, dm_id)
    assert dm_details_request.status_code == AccessError

def test_dm_details_v1_dm_id_is_non_valid_dm(reg_user, InputError): 
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_create_v1(token_sender, [auth_user_id_receiver])
    fake_dm_id = 9000
    
    dm_details_request = dm_details_v1(token_sender, fake_dm_id)
    assert dm_details_request.status_code == InputError

def test_dm_details_v1_auth_user_not_a_member_of_dm(reg_user, AccessError):
    clear_v2()
    token_sender= reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    token_non_auth_user = reg_user(2)['token']
    #u_id = [auth_user_id_receiver]
    dm_id = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    #dm_members = [auth_user_id_sender, auth_user_id_receiver] # create a list with the ids of the users 
    
    dm_details_request = dm_details_v1(token_non_auth_user, dm_id) #since this user was never appart of the dm he cant access info to it 
    assert dm_details_request.status_code == AccessError

def test_dm_details_v1_basic(reg_user): 
    clear_v2()
    user_register_sender = reg_user(0) #sender 
    user_register_receiver = reg_user(1) #receiver
    dm = dm_create_v1(user_register_sender['token'], [user_register_receiver['auth_user_id']])
    dm_members = [user_register_sender['auth_user_id'], user_register_receiver['auth_user_id']] # create a list with the ids of the users 
    dm_details = dm_details_v1(user_register_sender['token'], dm['dm_id'])
    for user in dm_details['members']:
        assert user['u_id'] in dm_members
    assert dm_details['members'][0]['email'] == 'example0@email.com'
    assert dm_details['members'][0]['name_first'] == 'firstname0'
    assert dm_details['members'][0]['name_last'] == 'lastname0'
    assert dm_details['members'][1]['email'] == 'example1@email.com'
    assert dm_details['members'][1]['name_first'] == 'firstname1'
    assert dm_details['members'][1]['name_last'] == 'lastname1'
    #assert dm_details['handle_str'] == f'lastname{i}
    assert dm_details['name'] == dm['dm_name'] 


