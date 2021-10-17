import pytest

from http_tests.route_wrappers_test import *
from src.config import url

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"fname{num}", f"lname{num}")
    return _register_user

#@pytest.fixture
#def u_handle(num):
    #return f"firstname{num}lastname{num}"
@pytest.fixture
def AccessError():
    return 403
    
def test_user_all_v1_token(reg_user, AccessError): 
    clear_v2()
    reg_user(0)
    fake_token = 'garbage values eafqwr34veewvsv'
    users_all_request = users_all_v1(fake_token)
    assert users_all_request.status_code == AccessError


    #assert that the list is the correct size if user 1 and 2 is found 
    #test what happens when they are only 1 user
    #test if there are heaps // use loops 
    #check all return cases // use fixtures 

def tests_users_all_v1_single_user(reg_user):
    clear_v2()
    user_register = reg_user(0)
    users_info = users_all_v1(user_register['token'])['users']
    assert users_info[0]['u_id'] == user_register['auth_user_id']
    assert users_info[0]['email'] == 'example0@email.com'
    assert users_info[0]['name_first'] == 'fname0'
    assert users_info[0]['name_last'] == 'lname0'
    assert users_info[0]['handle_str'] == 'fname0lname0'
    assert users_info[0]['profile_img_url'] == url + 'static/profile_photos/default.jpg'

def test_users_all_v1_multiple(reg_user):
    clear_v2()
    u_id_list = []
    user_register = reg_user(0)
    u_id_list.append(user_register['auth_user_id'])
    for i in range(1, 15):
        user_register_id = reg_user(i)['auth_user_id']
        u_id_list.append(user_register_id)
    users_info = users_all_v1(user_register['token'])['users']
    user_list = []
    #make 15 versions of what the infomtion should be 
    for i in range(0, 15):
        user_dict = {}
        user_dict['email'] = f"example{i}@email.com"
        user_dict['firstname'] = f"fname{i}"
        user_dict['lastname'] = f"lname{i}"
        user_dict['handle'] = f"fname{i}lname{i}"
        user_dict['profile_img_url'] = url + 'static/profile_photos/default.jpg'
        user_list.append(user_dict)
    
    #check that they all match 
    for i in range(0, 15): 
        assert users_info[i]['u_id'] in u_id_list
        assert user_list[i]['email'] == users_info[i]['email']
        assert user_list[i]['firstname'] == users_info[i]['name_first']
        assert user_list[i]['lastname'] == users_info[i]['name_last']
        assert user_list[i]['handle'] == users_info[i]['handle_str']
        assert user_list[i]['profile_img_url'] == users_info[i]['profile_img_url']

# Test that a removed user doesn't show up in the list of all users
def test_removed_user(reg_user):
    clear_v2()
    token = reg_user(0)['token']

    u_id_2 = reg_user(1)['auth_user_id']

    admin_user_remove_v1(token, u_id_2) # Remove second user

    assert len(users_all_v1(token)['users']) == 1
    