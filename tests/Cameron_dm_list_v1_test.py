import pytest

from src.other import clear_v2
from src.auth import auth_register_v2
from src.dm import dm_create_v1, dm_list_v1, dm_details_v1
from src.error import InputError, AccessError

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

def test_dm_list_v1_token(reg_user): 
    clear_v2()
    token_sender = reg_user(0)['token']
    auth_user_id_receiver = reg_user(1)['auth_user_id']
    dm_create_v1(token_sender, [auth_user_id_receiver])
    fake_token = 'garbage values' 
    
    with pytest.raises(AccessError):
        dm_list_v1(fake_token)

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
