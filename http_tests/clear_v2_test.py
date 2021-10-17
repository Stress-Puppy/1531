import pytest

from http_tests.route_wrappers_test import *

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def crt_channel():
    def _create_channel(token, num, is_public):
        return channels_create_v2(token, f'channel_{num}', is_public)
    return _create_channel

def test_single_user_and_channel(reg_user, crt_channel): # Test clearing of a single channel from the channels dictionary
    clear_v2()
    auth_user_token = reg_user(0)['token']
    crt_channel(auth_user_token, 0, True)
    clear_v2()
    auth_user_token =reg_user(0)['token']
    assert channels_listall_v2(auth_user_token)['channels'] == []

def test_single_user_multi_channel(reg_user, crt_channel): # Test clearing of multiple channels from the channels dictionary
    clear_v2()
    auth_user_token = reg_user(0)['token']
    for i in range(5):
        crt_channel(auth_user_token, i, i%2==0)
    clear_v2()
    auth_user_token = reg_user(0)['token']
    assert channels_listall_v2(auth_user_token)['channels'] == []

def test_no_initial_data(reg_user): # Test clearing with no data added to users or channels dictionary
    clear_v2()
    auth_user_token = reg_user(0)['token']
    assert channels_listall_v2(auth_user_token)['channels'] == []