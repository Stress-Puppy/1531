import sys
from json import dumps, dump
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src.error import InputError
from src.channels import channels_list_v2, channels_listall_v2, channels_create_v2
from src.dm import dm_messages_v1, dm_invite_v1, dm_remove_v1, dm_details_v1, dm_leave_v1, dm_create_v1, dm_list_v1
from src.message import message_send_v2, message_remove_v1, message_edit_v2, message_share_v1, message_senddm_v1, message_pin_v1, message_unpin_v1, message_react_v1, message_unreact_v1, message_sendlater_v1, message_sendlaterdm_v1
from flask_mail import Mail, Message

from src.notifications import notifications_get_v1
from src.other import clear_v2, search_v2
from src.users import users_all_v1, users_stats_v1

from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.admin import admin_userpermission_change_v1, admin_user_remove_v1
from src.channel import channel_details_v2, channel_invite_v2, channel_addowner_v1, channel_removeowner_v1, channel_leave_v1, channel_join_v2, channel_messages_v2
from src.helpers import read_data, write_data, erase_data, package_data, find_channel, find_dm

from src.user import user_profile_v2, user_profile_setname_v2, user_profile_sethandle_v1, user_profile_setemail_v1, user_stats_v1, user_profile_uploadphoto_v1
from src.standup import standup_start_v1, standup_active_v1, standup_send_v1

from src import config
from datetime import datetime, timezone
from src.data import messages, future_messages, reset_codes
import threading
from time import sleep


def data_persistence_handler():
    while True:
        sleep(5)
        erase_data()
        write_data()

def standup_handler(author_token, channel_id, duration):
    sleep(duration)
    channel_standup = find_channel(channel_id)['standup']
    channel_standup['is_active'] = False
    bundled_message = ''
    for msg in channel_standup['messages']:
        bundled_message += f"{msg['author_handle']}: {msg['message']}\n"
    message_send_v2(author_token, channel_id, bundled_message)

def sendlater_handler(message_id, time_sent):
    global messages, future_messages
    time_sent_dt = datetime.utcfromtimestamp(time_sent)
    now_dt = datetime.utcnow()
    duration = (time_sent_dt - now_dt).total_seconds()
    sleep(duration)
    for msg in list(future_messages):
        if msg['message_id'] == message_id:
            messages.append(msg)
            target_channel = find_channel(msg['channel_id'])
            target_channel['messages'].append(message_id)
            future_messages.remove(msg)

def sendlaterdm_handler(message_id, time_sent):
    global messages, future_messages
    time_sent_dt = datetime.utcfromtimestamp(time_sent)
    now_dt = datetime.utcnow()
    duration = (time_sent_dt - now_dt).total_seconds()
    sleep(duration)
    for msg in list(future_messages):
        if msg['message_id'] == message_id:
            messages.append(msg)
            target_dm = find_dm(msg['dm_id'])
            target_dm['messages'].append(message_id)
            future_messages.remove(msg)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_folder= '../static/', static_url_path='/static/')
CORS(APP)

APP.config['MAIL_SERVER']='smtp.gmail.com'
APP.config['MAIL_PORT'] = 587
APP.config['MAIL_USERNAME'] = 'wed11bcactus@gmail.com'
APP.config['MAIL_PASSWORD'] = 'iteration3'
APP.config['MAIL_USE_TLS'] = True
APP.config['MAIL_USE_SSL'] = False
mail = Mail(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

@APP.route("/static/<path:path>")
def send_file(path):
    return send_from_directory("", path)

@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def userpermission_change():
    parameters = request.get_json()
    token = parameters['token']
    u_id = parameters['u_id']
    permission_id = parameters['permission_id']
    output = admin_userpermission_change_v1(token, u_id, permission_id)
    return dumps(output)

@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def userpermission_remove():
    parameters = request.get_json()
    token = parameters['token']
    u_id = parameters['u_id']
    output = admin_user_remove_v1(token, u_id)
    return dumps(output)

@APP.route("/auth/logout/v1", methods=['POST'])
def logout():
    parameters = request.get_json()
    token = parameters['token']
    output = auth_logout_v1(token)
    return dumps(output)

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite():
    parameters = request.get_json()
    token = parameters['token']
    channel_id = parameters['channel_id']
    u_id = parameters['u_id']
    output = channel_invite_v2(token, channel_id, u_id)
    return dumps(output)

@APP.route("/channel/details/v2", methods=['GET'])
def channel_details():
    parameters = request.args
    token = parameters['token']
    channel_id = int(parameters['channel_id'])
    output = channel_details_v2(token, channel_id)
    return dumps(output)

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    parameters = request.args
    token = parameters['token']
    channel_id = int(parameters['channel_id'])
    start = int(parameters['start'])
    output = channel_messages_v2(token, channel_id, start)
    return dumps(output)

@APP.route("/channel/join/v2", methods=['POST'])
def channel_join():
    parameters = request.get_json()
    token = parameters['token']
    channel_id = parameters['channel_id']
    output = channel_join_v2(token, channel_id)
    return dumps(output)

@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    parameters = request.get_json()
    token = parameters['token']
    channel_id = parameters['channel_id']
    u_id = parameters['u_id']
    output = channel_addowner_v1(token, channel_id, u_id)
    return dumps(output)

@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    parameters = request.get_json()
    token = parameters['token']
    channel_id = parameters['channel_id']
    u_id = parameters['u_id']
    output = channel_removeowner_v1(token, channel_id, u_id)
    return dumps(output)

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    parameters = request.get_json()
    token = parameters['token']
    channel_id = parameters['channel_id']
    output = channel_leave_v1(token, channel_id)
    return dumps(output)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route("/auth/login/v2", methods=['POST'])
def login():
    parameters = request.get_json()
    email = parameters['email']
    password = parameters['password']
    output = auth_login_v2(email, password)
    return dumps(output)

@APP.route("/auth/register/v2", methods=['POST'])
def register():
    parameters = request.get_json()
    email = parameters['email']
    password = parameters['password']
    name_first = parameters['name_first']
    name_last = parameters['name_last']
    output = auth_register_v2(email, password, name_first, name_last)
    return dumps(output)

@APP.route("/channels/list/v2", methods=['GET'])
def channels_list():
    parameters = request.args
    token = parameters['token']
    
    output = channels_list_v2(token)
    return dumps(output) 
    
@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall():
    parameters = request.args
    token = parameters['token']
    output = channels_listall_v2(token)
    return dumps(output)
    

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create():
    parameters = request.get_json()
    token = parameters['token']
    name = parameters['name']
    is_public = parameters['is_public']
    output = channels_create_v2(token, name, is_public)
    return dumps(output)
    
@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages(): 
    parameters = request.args
    token = parameters['token']
    dm_id = int(parameters['dm_id'])
    start = int(parameters['start'])
    output = dm_messages_v1(token, dm_id, start)
    return dumps(output) 

@APP.route("/dm/invite/v1", methods=['POST'])
def dm_invite():
    parameters = request.get_json()
    token = parameters['token']
    dm_id = parameters['dm_id']
    u_id = parameters['u_id']
    dm_invite_v1(token, dm_id, u_id)
    return dumps({})

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove(): 
    parameters = request.get_json()
    token = parameters['token']
    dm_id = parameters['dm_id']
    dm_remove_v1(token, dm_id)
    return dumps({})

@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    parameters = request.args
    token = parameters['token']
    dm_id = int(parameters['dm_id'])
    output = dm_details_v1(token, dm_id)
    return dumps(output)

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    parameters = request.get_json()
    token = parameters['token']
    dm_id = parameters['dm_id']
    dm_leave_v1(token, dm_id)
    return dumps({})

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create(): 
    parameters = request.get_json()
    token = parameters['token']
    u_ids = parameters['u_ids']
    output = dm_create_v1(token, u_ids)
    return dumps(output) 
    
@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    parameters = request.args
    token = parameters['token']
    output = dm_list_v1(token)
    return dumps(output)

@APP.route("/message/send/v2", methods=['POST'])
def message_send():
    parameters = request.get_json()
    token = parameters['token']
    channel_id = parameters['channel_id']
    message = parameters['message']
    output = message_send_v2(token, channel_id, message)
    return dumps(output)
    
@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    parameters = request.get_json()
    token = parameters['token']
    message_id = parameters['message_id']
    message_remove_v1(token, message_id)
    return dumps({})

@APP.route("/message/edit/v2", methods=['PUT'])
def message_edit():
    parameters = request.get_json()
    token = parameters['token']
    message_id = parameters['message_id']
    message = parameters['message']
    message_edit_v2(token, message_id, message)
    return dumps({})

@APP.route("/message/share/v1", methods=['POST'])
def message_share():
    parameters = request.get_json()
    token = parameters['token']
    og_message_id = parameters['og_message_id']
    message = parameters['message']
    channel_id = parameters['channel_id']
    dm_id = parameters['dm_id']
    output = message_share_v1(token, og_message_id, message, channel_id, dm_id)
    return dumps(output)

@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm():
    parameters = request.get_json()
    token = parameters['token']
    dm_id = parameters['dm_id']
    message = parameters['message']
    output = message_senddm_v1(token, dm_id, message)
    return dumps(output)

@APP.route("/notifications/get/v1", methods=['GET'])
def notification():
    parameters = request.args
    token = parameters['token']
    output = notifications_get_v1(token)
    return dumps(output)

@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    output = clear_v2()
    return dumps(output)

@APP.route("/search/v2", methods=['GET'])
def search():
    parameters = request.args
    token = parameters['token']
    query_str = parameters['query_str']
    output = search_v2(token, query_str)
    return dumps(output)

@APP.route("/users/all/v1", methods=['GET'])
def users():
    parameters = request.args
    token = parameters['token']
    output = users_all_v1(token)
    return dumps(output)

@APP.route("/users/stats/v1", methods=['GET'])
def dreams_stats():
    parameters = request.args
    token = parameters['token']
    output = users_stats_v1(token)
    return dumps(output)

@APP.route("/user/profile/v2", methods=['GET'])
def profile():
    parameters = request.args
    token = parameters['token']
    u_id = int(parameters['u_id'])
    output = user_profile_v2(token, u_id)
    return dumps(output)

@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    parameters = request.get_json()
    token = parameters['token']
    channel_id = parameters['channel_id']
    length = parameters['length']
    output = standup_start_v1(token, channel_id, length)
    standup_thread = threading.Thread(target=standup_handler, args=[token, channel_id, length])
    standup_thread.start()
    return dumps(output)

@APP.route("/user/profile/setname/v2", methods=['PUT'])
def setname():
    parameters = request.get_json()
    token = parameters['token']
    name_first = parameters['name_first']
    name_last = parameters['name_last']
    output = user_profile_setname_v2(token, name_first, name_last)
    return dumps(output)

@APP.route("/user/profile/setemail/v2", methods=['PUT'])
def setemail():
    parameters = request.get_json()
    token = parameters['token']
    email = parameters['email']
    output = user_profile_setemail_v1(token, email)
    return dumps(output)

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def sethandle():
    parameters = request.get_json()
    token = parameters['token']
    handle_str = parameters['handle_str']
    output = user_profile_sethandle_v1(token, handle_str)
    return dumps(output)

@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater():
    parameters = request.get_json()
    token = parameters['token']
    channel_id = parameters['channel_id']
    message = parameters['message']
    time_sent = parameters['time_sent']
    output = message_sendlater_v1(token, channel_id, message, time_sent)
    message_id = output['message_id']
    standup_thread = threading.Thread(target=sendlater_handler, args=[message_id, time_sent])
    standup_thread.start()
    return dumps(output)


@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_sendlaterdm():
    parameters = request.get_json()
    token = parameters['token']
    dm_id = parameters['dm_id']
    message = parameters['message']
    time_sent = parameters['time_sent']
    output = message_sendlaterdm_v1(token, dm_id, message, time_sent)
    message_id = output['message_id']
    standup_thread = threading.Thread(target=sendlaterdm_handler, args=[message_id, time_sent])
    standup_thread.start()
    return dumps(output)

@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def passwordreset_request():
# i need to get the email
    parameters = request.get_json()
    email = parameters['email']
    auth_passwordreset_request_v1(email)
    name, code = ("","")
    for details in reset_codes:
        if details['email'] == email:
            name, code = (details['name'], details['code'])
    msg = Message('Reset Password Request for Dreams', sender =   'wed11bcactus@gmail.com', recipients = [email])
    dev_email = "wed11bcactus@gmail.com"
    msg.body = f'''Hey {name}\nYou have requested a password change for Dreams, 
please use the code provided to reset your password\n\nCODE:  
{code}\n\nIf you did not request a change of password please contact the dreams development 
team at\n*** {dev_email} ***\n\nKind Regards\n\nDreams Dev Team\nwed11bcactus'''
    mail.send(msg)
    return dumps({})

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def passwordreset_reset():
    parameters = request.get_json()
    reset_code = parameters['reset_code']
    new_password = parameters['new_password']
    auth_passwordreset_reset_v1(reset_code, new_password)
    return dumps({})

@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def uploadphoto():
    parameters = request.get_json()
    token = parameters['token']
    img_url = parameters['img_url']
    x_start = parameters['x_start']
    y_start = parameters['y_start']
    x_end = parameters['x_end']
    y_end = parameters['y_end']
    output = user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end)
    return dumps(output)

@APP.route("/message/react/v1", methods=['POST'])
def message_react():
    parameters = request.get_json()
    token = parameters['token']
    message_id = parameters['message_id']
    react_id = parameters['react_id']
    output = message_react_v1(token, message_id, react_id)
    return dumps(output)

@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact():
    parameters = request.get_json()
    token = parameters['token']
    message_id = parameters['message_id']
    react_id = parameters['react_id']
    output = message_unreact_v1(token, message_id, react_id)
    return dumps(output)

@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():
    parameters = request.args
    token = parameters['token']
    channel_id = int(parameters['channel_id'])
    output = standup_active_v1(token, channel_id)
    return dumps(output)

@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    parameters = request.get_json()
    token = parameters['token']
    channel_id = parameters['channel_id']
    message = parameters['message']
    output = standup_send_v1(token, channel_id, message)
    return dumps(output)

@APP.route("/user/stats/v1", methods=['GET'])
def user_stats():
    parameters = request.args
    token = parameters['token']
    output = user_stats_v1(token)
    return dumps(output)

@APP.route("/message/pin/v1", methods=['POST'])
def message_pin():
    parameters = request.get_json()
    token = parameters['token']
    message_id = parameters['message_id']
    message_pin_v1(token, message_id)
    return dumps({})
    
@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin():
    parameters = request.get_json()
    token = parameters['token']
    message_id = parameters['message_id']
    message_unpin_v1(token, message_id)
    return dumps({})

if __name__ == "__main__":
    read_data()
    persistence_thread = threading.Thread(target=data_persistence_handler)
    persistence_thread.start()
    APP.run(port=config.port) # Do not edit this port
