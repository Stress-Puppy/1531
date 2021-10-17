import requests
from src.config import url

'''
THIS IS THE FILE FOR ROUTE WRAPPERS, WHERE IT WILL ENABLE JSON FUNCTIONALITY TO OUR TESTS, 
WE STORE THE HTTP REQUEST EQUIVALENT FOR EACH FUNCTION SO WE CAN RUN EVERY TEST
'''

def auth_register_v2(email, password, name_first, name_last):
    # POST
    request = requests.post(url + 'auth/register/v2', json={ 'email': email, 
                                                          'password': password,
                                                          'name_first' : name_first,
                                                          'name_last' : name_last })
    output = request.json() if request.status_code == 200 else request
    return output

def auth_login_v2(email, password):
    # POST
    request = requests.post(url + 'auth/login/v2', json={'email': email, 'password': password})
    output = request.json() if request.status_code == 200 else request
    return output

def auth_logout_v1(token):
    # POST
    request = requests.post(url + 'auth/logout/v1', json={'token' : token})
    output = request.json() if request.status_code == 200 else request
    return output

def channel_invite_v2(token, channel_id, u_id):
    # POST
    request = requests.post(url + 'channel/invite/v2', json={'token' : token, 'channel_id' : channel_id, 'u_id' : u_id})
    output = request.json() if request.status_code == 200 else request
    return output

def channel_details_v2(token, channel_id):
    # GET
    request = requests.get(url + 'channel/details/v2', params={'token' : token, 'channel_id' : channel_id})
    output = request.json() if request.status_code == 200 else request
    return output

def channel_messages_v2(token, channel_id, start):
    # GET
    request = requests.get(url + 'channel/messages/v2', params={'token' : token, 'channel_id' : channel_id, 'start' : start})
    output = request.json() if request.status_code == 200 else request
    return output

def channel_join_v2(token, channel_id):
    # POST
    request = requests.post(url + 'channel/join/v2', json={'token' : token, 'channel_id' : channel_id})
    output = request.json() if request.status_code == 200 else request
    return output

def channel_addowner_v1(token, channel_id, u_id):
    # POST
    request = requests.post(url + 'channel/addowner/v1', json={'token' : token, 'channel_id' : channel_id, 'u_id' : u_id})
    output = request.json() if request.status_code == 200 else request
    return output

def channel_removeowner_v1(token, channel_id, u_id):
    # POST
    request = requests.post(url + 'channel/removeowner/v1', json={'token' : token, 'channel_id' : channel_id, 'u_id' : u_id})
    output = request.json() if request.status_code == 200 else request
    return output

def channel_leave_v1(token, channel_id):
    # POST
    request = requests.post(url + 'channel/leave/v1', json={'token' : token, 'channel_id' : channel_id})
    output = request.json() if request.status_code == 200 else request
    return output

def channels_list_v2(token):
    # GET
    request = requests.get(url + 'channels/list/v2', params={'token' : token})
    output = request.json() if request.status_code == 200 else request
    return output

def channels_listall_v2(token):
    # GET
    request = requests.get(url + 'channels/listall/v2', params={'token' : token})
    output = request.json() if request.status_code == 200 else request
    return output

def channels_create_v2(token, name, is_public):
    # POST
    request = requests.post(url + 'channels/create/v2', json={'token' : token, 'name' : name, 'is_public' : is_public})
    output = request.json() if request.status_code == 200 else request
    return output

def message_send_v2(token, channel_id, message):
    # POST
    request = requests.post(url + 'message/send/v2', json={'token' : token, 'channel_id' : channel_id, 'message' : message})
    output = request.json() if request.status_code == 200 else request
    return output

def message_edit_v2(token, message_id, message):
    # PUT
    request = requests.put(url + 'message/edit/v2', json={'token' : token, 'message_id' : message_id, 'message' : message})
    output = request.json() if request.status_code == 200 else request
    return output

def message_remove_v1(token, message_id):
    # DELETE
    request = requests.delete(url + 'message/remove/v1', json={'token' : token, 'message_id' : message_id})
    output = request.json() if request.status_code == 200 else request
    return output

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    # POST
    request = requests.post(url + 'message/share/v1', json={'token' : token, 
                                                          'og_message_id' : og_message_id,
                                                          'message' : message,
                                                          'channel_id' : channel_id,
                                                          'dm_id' : dm_id})
    output = request.json() if request.status_code == 200 else request
    return output

def dm_details_v1(token, dm_id):
    # GET
    request = requests.get(url + 'dm/details/v1', params={'token' : token, 'dm_id' : dm_id})
    output = request.json() if request.status_code == 200 else request
    return output

def dm_list_v1(token):
    # GET
    request = requests.get(url + 'dm/list/v1', params={'token' : token})
    output = request.json() if request.status_code == 200 else request
    return output

def dm_create_v1(token, u_id):
    # POST
    request = requests.post(url + 'dm/create/v1', json={'token' : token, 'u_ids' : u_id})
    output = request.json() if request.status_code == 200 else request
    return output

def dm_remove_v1(token, dm_id):
    # DELETE
    request = requests.delete(url + 'dm/remove/v1', json={'token' : token, 'dm_id' : dm_id})
    output = request.json() if request.status_code == 200 else request
    return output

def dm_invite_v1(token, dm_id, u_id):
    # POST
    request = requests.post(url + 'dm/invite/v1', json={'token' : token, 'dm_id' : dm_id, 'u_id' : u_id})
    output = request.json() if request.status_code == 200 else request
    return output

def dm_leave_v1(token, dm_id):
    # POST
    request = requests.post(url + 'dm/leave/v1', json={'token' : token, 'dm_id' : dm_id})
    output = request.json() if request.status_code == 200 else request
    return output

def dm_messages_v1(token, dm_id, start):
    # GET
    request = requests.get(url + 'dm/messages/v1', params={'token' : token, 'dm_id' : dm_id, 'start' : start})
    output = request.json() if request.status_code == 200 else request
    return output

def message_senddm_v1(token, dm_id, message):
    # POST
    request = requests.post(url + 'message/senddm/v1', json={'token' : token, 'dm_id' : dm_id, 'message' : message})
    output = request.json() if request.status_code == 200 else request
    return output

def user_profile_v2(token, u_id):
    # GET
    request = requests.get(url + 'user/profile/v2', params={'token' : token, 'u_id' : u_id})
    output = request.json() if request.status_code == 200 else request
    return output

def user_profile_setname_v2(token, name_first, name_last):
    # PUT
    request = requests.put(url + 'user/profile/setname/v2', json={'token' : token, 
                                                                 'name_first' : name_first,
                                                                 'name_last': name_last})
    output = request.json() if request.status_code == 200 else request
    return output

def user_profile_setemail_v1(token, email):
    # PUT
    request = requests.put(url + 'user/profile/setemail/v2', json={'token' : token, 'email' : email})
    output = request.json() if request.status_code == 200 else request
    return output

def user_profile_sethandle_v1(token, handle_str):
    # PUT
    request = requests.put(url + 'user/profile/sethandle/v1', json={'token' : token, 'handle_str' : handle_str})
    output = request.json() if request.status_code == 200 else request
    return output

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    # POST
    request = requests.post(url + 'user/profile/uploadphoto/v1', json={'token' : token,
                                                                        'img_url' : img_url,
                                                                        'x_start' : x_start,
                                                                        'y_start' : y_start,
                                                                        'x_end' : x_end,
                                                                        'y_end' : y_end})
    output = request.json() if request.status_code == 200 else request
    return output

def user_stats_v1(token):
    # GET
    request = requests.get(url + 'user/stats/v1', params={'token' : token})
    output = request.json() if request.status_code == 200 else request
    return output

def users_all_v1(token):
    # GET
    request = requests.get(url + 'users/all/v1', params={'token' : token})
    output = request.json() if request.status_code == 200 else request
    return output

def users_stats_v1(token):
    # GET
    request = requests.get(url + 'users/stats/v1', params={'token' : token})
    output = request.json() if request.status_code == 200 else request
    return output

def search_v2(token, query_str):
    # GET
    request = requests.get(url + 'search/v2', params={'token' : token, 'query_str' : query_str})
    output = request.json() if request.status_code == 200 else request
    return output

def admin_user_remove_v1(token, u_id):
    # DELETE
    request = requests.delete(url + 'admin/user/remove/v1', json={'token' : token, 'u_id' : u_id})
    output = request.json() if request.status_code == 200 else request
    return output

def admin_userpermission_change_v1(token, u_id, permission_id):
    # POST
    request = requests.post(url + 'admin/userpermission/change/v1', json={'token' : token, 
                                                                        'u_id' : u_id, 
                                                                        'permission_id' : permission_id})
    output = request.json() if request.status_code == 200 else request
    return output

def notifications_get_v1(token):
    # GET
    request = requests.get(url + 'notifications/get/v1', params={'token' : token})
    output = request.json() if request.status_code == 200 else request
    return output

def message_unpin_v1(token, message_id):
    # POST
    request = requests.post(url + 'message/unpin/v1', json={'token' : token, 'message_id' : message_id})
    
    output = request.json() if request.status_code == 200 else request
    return output

def message_pin_v1(token, message_id):
    # POST
    request = requests.post(url + 'message/pin/v1', json={'token': token, 'message_id': message_id})
    output = request.json() if request.status_code == 200 else request
    return output
    
def standup_active_v1(token, channel_id):
    #GET
    request = requests.get(url + 'standup/active/v1', params={'token' : token, 
                                                              'channel_id' : channel_id })
    output = request.json() if request.status_code == 200 else request
    return output

def standup_start_v1(token, channel_id, length):
    # POST
    request = requests.post(url + 'standup/start/v1', json={'token' : token, 'channel_id' : channel_id, 'length' : length})
    output = request.json() if request.status_code == 200 else request
    return output
    
def standup_send_v1(token, channel_id, message):
    # POST
    request = requests.post(url + 'standup/send/v1', json={'token' : token, 'channel_id' : channel_id, 'message' : message})
    output = request.json() if request.status_code == 200 else request
    return output

def auth_passwordreset_request_v1(email):
    # POST 
    request = requests.post(url + 'auth/passwordreset/request/v1', json={'email' : email})
    output = request.json() if request.status_code == 200 else request
    return output 

def auth_passwordreset_reset_v1(reset_code, new_password):
    # POST 
    request = requests.post(url + 'auth/passwordreset/reset/v1', json={'reset_code' : reset_code, 'new_password' : new_password})
    output = request.json() if request.status_code == 200 else request
    return output 

def clear_v2():
    # DELETE
    request = requests.delete(url + 'clear/v1')
    output = request.json() if request.status_code == 200 else request
    return output

def message_sendlater_v1(token, channel_id, message, time_sent):
    # POST
    request = requests.post(url + 'message/sendlater/v1', json={'token' : token, 
                                                                'channel_id' : channel_id, 
                                                                'message' : message,
                                                                'time_sent' : time_sent})
    output = request.json() if request.status_code == 200 else request
    return output

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    # POST
    request = requests.post(url + 'message/sendlaterdm/v1', json={'token' : token, 
                                                                'dm_id' : dm_id, 
                                                                'message' : message,
                                                                'time_sent' : time_sent})
    output = request.json() if request.status_code == 200 else request
    return output

def message_react_v1(token, message_id, react_id):
    # POST
    request = requests.post(url + 'message/react/v1', json={'token' : token, 
                                                            'message_id' : message_id, 
                                                            'react_id' : react_id})
    output = request.json() if request.status_code == 200 else request
    return output

def message_unreact_v1(token, message_id, react_id):
    # POST
    request = requests.post(url + 'message/unreact/v1', json={'token' : token, 
                                                            'message_id' : message_id, 
                                                            'react_id' : react_id})
    output = request.json() if request.status_code == 200 else request
    return output