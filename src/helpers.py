from src.data import next_u_id, users, next_channel_id, channels, next_dm_id, next_message_id, messages, dms, tokens, notifications, reset_codes, dreams_stats, SECRET
from src.error import InputError, AccessError
import re
from datetime import timezone
from datetime import datetime
import jwt
import hashlib
import pickle
import string
import random

def generate_token(u_id):
    """Summary
        Generates a user session token given a dictionary containing their user information. This token is
        added to the tokens list for later reference and returned for immediate use
    Args:
        user (dictionary): A dictionary containing all stored information about a user (a single element in
                           the users list)
    
    Returns:
        token (string): an encoded jwt string that can be used as a user session token
    """
    DATA = { 'u_id' : u_id, 'timestamp' : current_unix_timestamp()} 
    token = jwt.encode(DATA, SECRET, algorithm='HS256')
    tokens.append(token)
    return token

def check_token(token):
    """Summary
        Given a token string, verifies that it is one of the currently active user session tokens and
        that it can be decoded using the hidden SECRET string. If both of these conditions are true
    Args:
        token (string): A user session token (jwt)

    Returns:
        Boolean: True, only if the token is an active session token and can be decoded as expected
    
    Raises:
        AccessError: If the token is not in the list of current session tokens, or the token could not
                     be decoded as expected (occurs if token has been modified in any way)
    """
    if len(tokens) and token in tokens: # Verify that token exists in stored list of active user session tokens
        jwt.decode(token, SECRET, algorithms=['HS256'])
        return True
    else: # If token is not an active token, it is invalid
        raise AccessError("Invalid token, not in list of current session tokens")
    
def user_from_token(token):
    """Summary
        For a given token, decodes its stored user data, obtains the matching user's data dictionary from the 
        users list and returns it
    Args:
        token (string): A user session token
    
    Returns:
        Dictionary: Contains the user data of the user whose token was passed in
    
    Raises:
        AccessError: When the given token could not be decoded (this should never happen under normal operation,
                     since the check_token function will have been used beforehand)
        InputError: When a match for the user id retrieved from the decoded token could not be found in the
                    users list (this should also never happen during operation)
    """
    user_id = jwt.decode(token, SECRET, algorithms=['HS256'])['u_id']
    target_user = {}
    for user in users:
        if user['u_id'] == user_id:
            target_user = user
    return target_user
    
def is_dreams_owner(u_id):
    """Summary
        Determines whether or not a user is a Dreams owner
    Args:
        u_id (int): A user id number
    
    Returns:
        Boolean: True if the user with id u_id is a Dreams owner, False if the user
                 could not be found or they are not a Dreams owner
    """
    target_user = {}
    for user in users:
        if user['u_id'] == u_id: # Find user with id u_id
            target_user = user
    if target_user['permission'] == 1: # Check whether they have the owner permission
        return True # Return True if the user is an owner
    else:
        return False # Return False if the user is not an owner
    
def is_channel_owner(u_id, channel_id):
    """Summary
        Determines whether a user is the owner of a channel
    Args:
        u_id (int): A user id number
        channel_id (int): A channel id number
    
    Returns:
        Boolean: True if user is a channel owner, otherwise False
    """
    target_channel = {}
    for channel in channels:
        if channel['channel_id'] == channel_id:
            target_channel = channel
    if u_id in target_channel['owner_members']:
        return True
    else:
        return False

def is_channel_member(u_id, channel_id):
    """Summary
        Determines whether a user is the member of a channel
    Args:
        u_id (int): A user id number
        channel_id (int): A channel id number
    
    Returns:
        Boolean: True if user is a channel member, otherwise False
    """
    target_channel = {}
    for channel in channels:
        if channel['channel_id'] == channel_id:
            target_channel = channel
    if u_id in target_channel['all_members']:
        return True
    else:
        return False
    
def valid_email(email):
    """Summary
        Determines whether or not a given email string is valid
    Args:
        email (string): An email address string
    
    Returns:
        Boolean: True if email string is a valid email, False otherwise
    """
    return re.fullmatch('^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$', email)
    
def valid_channel(channel_id):
    for channel in channels:
        if channel['channel_id'] == channel_id:
            return True
    return False

def valid_dm(dm_id):
    for dm in dms:
        if dm['dm_id'] == dm_id:
            return True
    return False

def valid_message(message_id):
    for message in messages:
        if message['message_id'] == message_id:
            return True 
    return False
    
def user_from_id(u_id):
    """Summary
        Gets a user's user dictionary based on their user id
    Args:
        u_id (int): A user id number
    
    Returns:
        Dictionary: Contains all of the user's stored information if the user was found, otherwise empty
    """
    target_user = {}
    for user in users:
        if user['u_id'] == u_id:
            target_user = user
    return target_user

def current_unix_timestamp():
    dt = datetime.now(timezone.utc)
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    return timestamp

def get_hash(password):
    """Summary
        Given a password string, encodes it using a hash algorithm and returns the encoded string
    Args:
        password (string): A password
    
    Returns:
        string: The hash-encoded password argument
    """
    return hashlib.sha256(password.encode()).hexdigest()

def package_data():
    DATA_STRUCTURE = {
        'next_u_id' : next_u_id,
        'users' : users,
        'next_channel_id' : next_channel_id,
        'channels' : channels,
        'next_message_id' : next_message_id,
        'messages' : messages,
        'next_dm_id' : next_dm_id,
        'dms' : dms,
        'tokens' : tokens,
        'notifications' : notifications,
        'dreams_stats' : dreams_stats,
        'reset_codes' : reset_codes
    }
    return DATA_STRUCTURE
    
def write_data():
    """Summary
        Pickles, then writes, the current contents of the non-static data structures and 
        variables in data.py to data.p for the purpose of data persistence
    """
    DATA_STRUCTURE = package_data()

    with open('data.p', 'wb') as DATA_FILE:
        pickle.dump(DATA_STRUCTURE, DATA_FILE)

def read_data():
    """Summary
        Unpickles and reads stored variables and data structures from data.py, updating data of current
        backend instance.
    """
    global next_u_id, users, next_channel_id, channels, next_dm_id, next_message_id, messages, next_dm_id, dms, tokens, notifications, dreams_stats, reset_codes
    try:
        with open('data.p', 'rb') as DATA_FILE:
            DATA = pickle.load(DATA_FILE)

            next_u_id['id'] = DATA['next_u_id']['id']
            for user in DATA['users']:
                users.append(user)

            next_channel_id['id'] = DATA['next_channel_id']['id']
            for channel in DATA['channels']:
                channels.append(channel)

            next_message_id['id'] = DATA['next_message_id']['id']
            for message in DATA['messages']:
                messages.append(message)

            next_dm_id['id'] = DATA['next_dm_id']['id']
            for dm in DATA['dms']:
                dms.append(dm)
            
            for token in DATA['tokens']:
                tokens.append(token)

            for notification in DATA['notifications']:
                notifications.append(notification)

            dreams_stats['channels_exist'] = DATA['dreams_stats']['channels_exist']
            dreams_stats['dms_exist'] = DATA['dreams_stats']['dms_exist']
            dreams_stats['messages_exist'] = DATA['dreams_stats']['messages_exist']

            for code in DATA['reset_codes']:
                reset_codes.append(code)
    except:
        '''
        If an EOFError occurs, this is because the file is blank or there is
        insufficient written data to read into the data structures e.g. users, channels
        '''
        next_u_id['id'] = 0
        users.clear()

        next_channel_id['id'] = 0
        channels.clear()

        next_dm_id['id'] = 0
        dms.clear()

        next_message_id['id'] = 0
        messages.clear()

        tokens.clear()

        notifications.clear()

def erase_data():
    open('data.p', 'w').close() # Erase data from data.p file

def is_dm_member(dm_id, u_id):
    """Summary
        Determines whether or not a user is a Dreams menber
    Args:
        u_id (int): A user id number
    
    Returns:
        Boolean: True if the user with id u_id is a Dreams menber, False if the user
                 could not be found or they are not a Dreams menber
    """
    target_dm = {}
    for dm in dms:
        if dm['dm_id'] == dm_id:
            target_dm = dm
    if u_id in target_dm['members']:
        return True
    else:
        return False

def user_with_same_handle(handle_str):
    for user in users:
        if user['handle_str'] == handle_str:
            return True
    return False

def find_channel(channel_id):
    target_channel = {}
    for channel in channels: 
        if channel['channel_id'] == channel_id:
            target_channel = channel
    return target_channel

def valid_user(u_id):
    for user in users:
        if user['u_id'] == u_id and user['permission'] != 0:
            return True
    return False 

def get_message_from_message_id(message_id):
    target_message = {}
    for message in messages: 
        if message['message_id'] == message_id:
            target_message = message
    return target_message

def join_handle(user_list_handles):
    return ', '.join(sorted(user_list_handles))

# def find_dream_owner_user(u_id):
#     for user in users:
#         if user['u_id'] == u_id and user['permission'] == 1:
#             return user

def find_all_dream_owners():

    dream_owners = []

    for user in users:
        if user['permission'] == 1:
            dream_owners.append(user)
    return dream_owners

def find_dm(dm_id):
    target_dm = {}
    for dm in dms:
        if dm['dm_id'] == dm_id:
            target_dm = dm
    return target_dm

def send_channel_tag_notification(tagger_handle, taggee_id, channel_id, message):
    channel = find_channel(channel_id)
    tag_noti_text = f"{tagger_handle} tagged you in {channel['name']}: {message[:20]}"
    noti = {}
    noti['channel_id'] = channel_id
    noti['dm_id'] = -1
    noti['notification_message'] = tag_noti_text
    for noti_list in notifications:
        if noti_list['u_id'] == taggee_id:
            noti_list['notifications'].append(noti)

def send_dm_tag_notification(tagger_handle, taggee_id, dm_id, message):
    dm = find_dm(dm_id)
    tag_noti_text = f"{tagger_handle} tagged you in {dm['name']}: {message[:20]}"
    noti = {}
    noti['channel_id'] = -1
    noti['dm_id'] = dm_id
    noti['notification_message'] = tag_noti_text
    for noti_list in notifications:
        if noti_list['u_id'] == taggee_id:
            noti_list['notifications'].append(noti)

def send_channel_added_notification(adder_handle, addee_id, channel_id):
    channel = find_channel(channel_id)
    add_noti_text = f"{adder_handle} added you to {channel['name']}"
    noti = {}
    noti['channel_id'] = channel_id
    noti['dm_id'] = -1
    noti['notification_message'] = add_noti_text
    for noti_list in notifications:
        if noti_list['u_id'] == addee_id:
            noti_list['notifications'].append(noti)

def send_dm_added_notification(adder_handle, addee_id, dm_id):
    dm = find_dm(dm_id)
    add_noti_text = f"{adder_handle} added you to {dm['name']}"
    noti = {}
    noti['channel_id'] = -1
    noti['dm_id'] = dm_id
    noti['notification_message'] = add_noti_text
    for noti_list in notifications:
        if noti_list['u_id'] == addee_id:
            noti_list['notifications'].append(noti)

def send_channel_message_react_notification(reactor_id, author_id, channel_id):
    reactor_handle = user_from_id(reactor_id)['handle_str']

    channel_name = find_channel(channel_id)['name']

    noti_text = f"{reactor_handle} reacted to your message in {channel_name}"

    noti = {}
    noti['channel_id'] = channel_id
    noti['dm_id'] = -1
    noti['notification_message'] = noti_text

    for noti_list in notifications:
        if noti_list['u_id'] == author_id:
            noti_list['notifications'].append(noti)

def send_dm_message_react_notification(reactor_id, author_id, dm_id):
    reactor_handle = user_from_id(reactor_id)['handle_str']

    dm_name = find_dm(dm_id)['name']

    noti_text = f"{reactor_handle} reacted to your message in {dm_name}"

    noti = {}
    noti['channel_id'] = -1
    noti['dm_id'] = dm_id
    noti['notification_message'] = noti_text

    for noti_list in notifications:
        if noti_list['u_id'] == author_id:
            noti_list['notifications'].append(noti)

def update_channel_stats():
    num_channels_exist = len(channels)
    timestamp = current_unix_timestamp()
    data_dict = { 'num_channels_exist' : num_channels_exist, 'time_stamp' : timestamp }
    dreams_stats['channels_exist'].append(data_dict)

def update_dm_stats():
    num_dms_exist = len(dms)
    timestamp = current_unix_timestamp()
    data_dict = { 'num_dms_exist' : num_dms_exist, 'time_stamp' : timestamp }
    dreams_stats['dms_exist'].append(data_dict)

def update_message_stats():
    num_messages_exist = len(messages)
    timestamp = current_unix_timestamp()
    data_dict = { 'num_messages_exist' : num_messages_exist, 'time_stamp' : timestamp }
    dreams_stats['messages_exist'].append(data_dict)

def random_code_generator():
    password_length = 8
    strings_uppercase_chars_and_digits = string.ascii_uppercase + string.digits
    return ''.join(random.choice(strings_uppercase_chars_and_digits) for _ in range(password_length))

def update_user_channel_stats(u_id):
    user = user_from_id(u_id)

    data_dict = { 
                  'num_channels_joined' : len(user['channels']),
                  'time_stamp' : current_unix_timestamp() 
                }

    user['stats']['channels_joined'].append(data_dict)

def update_user_dm_stats(u_id):
    user = user_from_id(u_id)

    data_dict = { 
                  'num_dms_joined' : len(user['dms']),
                  'time_stamp' : current_unix_timestamp()
                }

    user['stats']['dms_joined'].append(data_dict)

def update_user_message_stats(u_id):
    user = user_from_id(u_id)

    messages_sent = 0
    for message in messages:
        if message['author_id'] == u_id:
            messages_sent += 1

    data_dict = { 
                  'num_messages_sent' : messages_sent,
                  'time_stamp' : current_unix_timestamp() 
                }

    user['stats']['messages_sent'].append(data_dict)

