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
    
def test_dm_list_v1_token(reg_user, AccessError): 
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_create_v1(token_sender, [auth_user_id_receiver])
    fake_token = 'garbage values' 
    
    dm_list_request = dm_list_v1(fake_token)
    dm_list_request.status_code = AccessError

def test_dm_list_v1_basic(reg_user):
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_id_create = dm_create_v1(token_sender, [auth_user_id_receiver])['dm_id']
    dm_list_checker = [dm_id_create]
    for i in range(2, 11): 
        auth_user_id_extra = reg_user(i)['auth_user_id']
        dm_id_extra = dm_create_v1(token_sender, [auth_user_id_extra])['dm_id']
        dm_list_checker.append(dm_id_extra)
    dms = dm_list_v1(token_sender)['dms']
    for dm in dms: #inside this whole list of dictonarys get this dictonary then check if the dm_id is in the list
        assert dm['dm_id'] in dm_list_checker

