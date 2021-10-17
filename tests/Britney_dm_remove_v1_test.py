import pytest

from src.other import clear_v2
from src.auth import auth_register_v2
from src.dm import dm_remove_v1, dm_create_v1, dm_invite_v1, dm_list_v1, dm_details_v1
from src.message import message_senddm_v1
from src.other import search_v2
from src.error import InputError, AccessError

# InputError when:   dm_id does not refer to a valid DM 
    
# AccessError when:  the user is not the original DM creator

# Remove an existing DM. This can only be done by the original creator of the DM.
    
# Parameters:(token, dm_id)
# Return Type:{}

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def crt_dm():
    def _create_dm(token, u_ids):
        return dm_create_v1(token, u_ids)
    return _create_dm

@pytest.fixture
def send_dm():
    def _send_dm(token, dm_id, message):
        return message_senddm_v1(token, dm_id, message)
    return _send_dm

# commom case
def test_commom_one(reg_user):
    clear_v2()
    user = reg_user(0)
    token = user['token']
    u_id = user['auth_user_id']

    # one dm id
    dm = dm_create_v1(token, [u_id])
    dm_id = dm['dm_id']
    
    dm_remove_v1(token, dm_id)

    dm_list = dm_list_v1(token)['dms']
    assert not len(dm_list)

    with pytest.raises(InputError):
        dm_details_v1(token, dm_id)

def test_commom_more(reg_user):
    clear_v2()
    user = reg_user(0)
    token = user['token']

    user_2 = reg_user(1)
    user_2_id = user_2['auth_user_id']

    # more dm id
    dm1 = dm_create_v1(token, [user_2_id])
    dm_id1 = dm1['dm_id']
    dm2 = dm_create_v1(token, [user_2_id])
    dm_id2 = dm2['dm_id']
    dm3 = dm_create_v1(token, [user_2_id])
    dm_id3 = dm3['dm_id']
    dm_remove_v1(token, dm_id1)
    dm_remove_v1(token, dm_id2)
    dm_remove_v1(token, dm_id3)

    dm_list = dm_list_v1(token)['dms']
    assert not len(dm_list)
    
    # dm become invaild
    with pytest.raises(InputError):
        dm_details_v1(token, dm_id1)
    with pytest.raises(InputError):
        dm_details_v1(token, dm_id2)
    with pytest.raises(InputError):
        dm_details_v1(token, dm_id3)

# invaile token 
def test_invalid_token(reg_user):
    
    clear_v2()
    first_user = reg_user(0)
    first_token = first_user['token']
    first_id = first_user['auth_user_id']
    dm = dm_create_v1(first_token, [first_id])
    dm_id = dm['dm_id']

    with pytest.raises(AccessError):
        dm_remove_v1("invalid_token", dm_id)


# AccessError when:  the user is not the original DM creator
def test_not_creator(reg_user):
    clear_v2()
    first_user = reg_user(0)
    first_token = first_user['token']
    first_id = first_user['auth_user_id']
    dm = dm_create_v1(first_token, [first_id])
    dm_id = dm['dm_id']

    second_user = reg_user(1)
    second_token = second_user['token']
    second_id = second_user['auth_user_id']
    dm_invite_v1(first_token, dm_id, second_id)

    # second user is not the original DM creator 
    with pytest.raises(AccessError):
        dm_remove_v1(second_token, dm_id)

def test_remove_dm_with_messages(reg_user, crt_dm, send_dm):
    clear_v2()

    user = reg_user(0)
    token = user['token']
    u_id = user['auth_user_id']

    message = "Apple"

    dm_id = crt_dm(token, [u_id])['dm_id']

    send_dm(token, dm_id, message) # Send message containing string "Apple"

    dm_remove_v1(token, dm_id)

    assert search_v2(token, message)['messages'] == []

# InputError when:   dm_id does not refer to a valid DM 
def test_invalid_dm_id(reg_user):
    clear_v2()
    user = reg_user(0)
    token = user['token']
    u_id = user['auth_user_id']
    dm = dm_create_v1(token, [u_id])
    dm_id = dm['dm_id']
    
    with pytest.raises(InputError):
        dm_remove_v1(token, dm_id + 1)

