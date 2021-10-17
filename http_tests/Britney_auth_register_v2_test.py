import pytest

from http_tests.route_wrappers_test import *

@pytest.fixture
def user_details(): 
    return ("akali@league.com", "goodpass123", "Shen", "Ionia")

@pytest.fixture
def InputError():
    return 400

# Error cases
# 1. email is not valid (use method in gitlab) 
def test_not_valid_email(InputError):
    clear_v2()
    email = "garen!league.com"
    pwd = "goodpass123"
    fName = "Garen"
    lName = "Demacia"
    register_request = auth_register_v2(email, pwd, fName, lName)
    assert register_request.status_code == InputError
    # Invalid email format (no @)

# 2. email is already being used
def test_already_used_email(user_details, InputError):
    clear_v2()
    email, pwd, fName, lName = user_details
    auth_register_v2(email, pwd, fName, lName)
    register_request = auth_register_v2(email, pwd, fName, lName)
    assert register_request.status_code == InputError
    # Duplicate emails

# 3. password < 6 characters
def test_pass_too_short(InputError):
    clear_v2()
    email = "akali@league.com"
    pwd = "abc"
    fName = "Akali"
    lName = "Ionia"
    register_request = auth_register_v2(email, pwd, fName, lName)
    assert register_request.status_code == InputError

# 4. NOT 1 <= name_first, name_last length <= 50
# first name < 1 so error
def test_name_length_error1(InputError):
    clear_v2()
    email = "akali@league.com"
    pwd = "goodpass123"
    fName = ""
    lName = "Ionia"
    register_request = auth_register_v2(email, pwd, fName, lName)
    assert register_request.status_code == InputError

# long first name
def test_name_length_error2(InputError):
    clear_v2()
    email = "aatrox@league.com"
    pwd = "goodpass123"
    fName = "Now hear the silence of annihilation!They think me defeated, enchained. But I am unbowed... Noble is this carnage."
    lName = "Darkin"
    register_request = auth_register_v2(email, pwd, fName, lName)
    assert register_request.status_code == InputError

# no last name
def test_name_length_error3(InputError):
    clear_v2()
    email = "azir@league.com"
    pwd = "goodpass123"
    fName = "Azir"
    lName = ""
    register_request = auth_register_v2(email, pwd, fName, lName)
    assert register_request.status_code == InputError

# long last name
def test_name_length_error4(InputError):
    clear_v2()
    email = "azir@league.com"
    pwd = "goodpass123"
    fName = "Azir"
    lName = "Shurima! Your emperor has returned!Shurima will once again stretch to the horizon.\
            Shurima will once again stretch to the horizon.Shurima will once again stretch to the horizon."
    register_request = auth_register_v2(email, pwd, fName, lName)
    assert register_request.status_code == InputError

# 5. handle error 
#   repeat error
def test_handle_repeat():
    clear_v2()
    user1 = auth_register_v2("britney@league.com", "goodpass123", "Stress", "Puppy")
    user2 = auth_register_v2("britney2@league.com", "goodpass123", "Stress", "Puppy")
    user3 = auth_register_v2("britney3@league.com", "goodpass123", "Stress", "Puppy")
    
    user_1 = user_profile_v2(user1['token'], user1['auth_user_id'])['user']
    user_2 = user_profile_v2(user2['token'], user2['auth_user_id'])['user']
    user_3 = user_profile_v2(user3['token'], user3['auth_user_id'])['user']
        
 
    assert user_1['handle_str'] == "stresspuppy"
    assert user_2['handle_str'] == "stresspuppy0"
    assert user_3['handle_str'] == "stresspuppy1"

#   (concatenation length > 20)
#   Appending number -> might result in exceeding 20 character limit
def test_handle_cut_off_and_appengding_number():
    clear_v2()
    user1 = auth_register_v2("azir@league.com", "password", "azir", "thisIsLongerThanTwenty")
    user2 = auth_register_v2("azir1@league.com", "password", "azir", "thisIsLongerThanTwenty")
    
    user_1 = user_profile_v2(user1['token'], user1['auth_user_id'])['user']
    user_2 = user_profile_v2(user2['token'], user2['auth_user_id'])['user']
    
    assert user_1['handle_str'] == "azirthisislongerthan"
    assert user_2['handle_str'] == "azirthisislongerthan0"

#   handle including whitespace or @
def test_handle_invalid_char():
    clear_v2()
    user1 = auth_register_v2("shen@league.com", "goodpass123", "shen", "@ nia")
    
    user = user_profile_v2(user1['token'], user1['auth_user_id'])['user']
    assert user['handle_str'] == "shennia"
