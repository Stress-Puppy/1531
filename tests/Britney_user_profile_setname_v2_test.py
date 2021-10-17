import pytest

from src.auth import auth_register_v2
from src.user import user_profile_v2, user_profile_setname_v2
from src.other import clear_v2
from src.error import InputError, AccessError

# InputError when any of:
      
        # name_first is not between 1 and 50 characters inclusively in length
        # name_last is not between 1 and 50 characters inclusively in length

# Parameters: (token, name_first, name_last)
# Return Type: {}

# Update the authorised user's first and last name

# user_profile_setname_v2()

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

# invaile token 
def test_invalid_token(reg_user):

    clear_v2()
    name_first = "first"
    name_last = "second"

    with pytest.raises(AccessError):
        user_profile_setname_v2("invalid_token", name_first, name_last)

def test_first_name_non_string(reg_user):

    clear_v2()
    token = reg_user(0)['token']
    name_first = 1
    name_last = "second"

    with pytest.raises(InputError):
        user_profile_setname_v2(token, name_first, name_last)

def test_last_name_non_string(reg_user):

    clear_v2()
    token = reg_user(0)['token']
    name_first = "First"
    name_last = 1

    with pytest.raises(InputError):
        user_profile_setname_v2(token, name_first, name_last)

#         commom case 1 : change both first and last name
def test_both_change(reg_user):

    clear_v2()
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    name_first = 'stress'
    name_last = 'puppy'

    user_profile_setname_v2(user_token, name_first, name_last)

    user_details = user_profile_v2(user_token, user_id)['user']
    assert user_details['name_first'] == 'stress' 
    assert user_details['name_last'] == 'puppy'

#         commom case 2: only change first name
def test_change_first(reg_user):

    clear_v2()
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    user_details = user_profile_v2(user_token, user_id)['user']
    name_last = user_details['name_last']
    name_first = 'stress'

    user_profile_setname_v2(user_token, name_first, name_last)

    user_details = user_profile_v2(user_token, user_id)['user']
    assert user_details['name_first'] == 'stress' 
    assert user_details['name_last'] == name_last

#         commom case 3: only change last name
def test_change_last(reg_user):

    clear_v2()
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    user_details = user_profile_v2(user_token, user_id)['user']
    name_first = user_details['name_first']
    name_last = 'puppy'

    user_profile_setname_v2(user_token, name_first, name_last)

    user_details = user_profile_v2(user_token, user_id)['user']
    assert user_details['name_first'] == name_first 
    assert user_details['name_last'] == 'puppy'


# name_first is not between 1 and 50 characters inclusively in length
def test_length_fist_name(reg_user):
    clear_v2()
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    user_details = user_profile_v2(user_token, user_id)['user']
    name_last = user_details['name_last']
    name_first_short = ''
    name_first_long = 's'*100

    with pytest.raises(InputError):
        user_profile_setname_v2(user_token, name_first_short, name_last)
    with pytest.raises(InputError):
        user_profile_setname_v2(user_token, name_first_long, name_last)


# name_last is not between 1 and 50 characters inclusively in length
def test_length_last_name(reg_user):
    clear_v2()
    new_user = reg_user(0)
    user_token = new_user['token']
    user_id =  new_user['auth_user_id']
    user_details = user_profile_v2(user_token, user_id)['user']
    name_first = user_details['name_first']
    name_last_short = ''
    name_last_long = 's'*100

    with pytest.raises(InputError):
        user_profile_setname_v2(user_token, name_first, name_last_short)
    with pytest.raises(InputError):
        user_profile_setname_v2(user_token, name_first, name_last_long)


# name_first, name_last is not between 1 and 50 characters inclusively in length
def test_length_both_long(reg_user):
    
    clear_v2()
    user = reg_user(0)
    user_token = user['token']
    name_first_new = 'h'*100
    name_last_new = 'i'*100

    with pytest.raises(InputError):
        user_profile_setname_v2(user_token, name_first_new, name_last_new)

# name_first, name_last is not between 1 and 50 characters inclusively in length
def test_length_both_none(reg_user):
    
    clear_v2()
    user = reg_user(0)
    user_token = user['token']
    name_first_new = ''
    name_last_new = ''

    with pytest.raises(InputError):
        user_profile_setname_v2(user_token, name_first_new, name_last_new)

# name_first, name_last is not between 1 and 50 characters inclusively in length
def test_length_first_long(reg_user):
    
    clear_v2()
    user = reg_user(0)
    user_token = user['token']
    name_first_new = 'h'*100
    name_last_new = ''
    
    with pytest.raises(InputError):
        user_profile_setname_v2(user_token, name_first_new, name_last_new)

# name_first, name_last is not between 1 and 50 characters inclusively in length
def test_length_last_long(reg_user):
    
    clear_v2()
    user = reg_user(0)
    user_token = user['token']
    name_first_new = ''
    name_last_new = 'i'*100
    
    with pytest.raises(InputError):
        user_profile_setname_v2(user_token, name_first_new, name_last_new)


