import urllib.request
import requests
import os
import imgspy

from src.data import next_u_id, users, next_channel_id, channels, next_message_id, messages, dms, tokens, notifications
from src.helpers import check_token, user_from_token, valid_user, user_from_id, user_with_same_handle, valid_email, find_all_dream_owners, current_unix_timestamp
from src.error import InputError, AccessError
from src.config import url
from PIL import Image

def user_profile_v2(token, u_id):
    '''
    Summary:
        For a valid user, returns information about their 
        user_id, 
        email, 
        first name, 
        last name, 
        and handle
    Args:
        token (string): A user session token 
        u_id (int): A user id 
    Returns: 
        a dictionary which contains information about the user

    Raises:
        InputError when:
            User with u_id is not a valid user
    '''
    global users, channels, dms
    assert check_token(token)
    
    user_found = False
    for user in users:
        if user['u_id'] == u_id:
            user_found = True
            
    if not user_found:
        raise InputError(f"User with u_id is not a valid user")
    
    #only add wanted infomation to the returned dictionary 
    user_profile = user_from_id(u_id)
    user_wanted_info = {}
    user_wanted_info['u_id'] = user_profile['u_id']
    user_wanted_info['email'] = user_profile['email']
    user_wanted_info['name_first'] = user_profile['name_first']
    user_wanted_info['name_last'] = user_profile['name_last']
    user_wanted_info['handle_str'] = user_profile['handle_str']
    user_wanted_info['profile_img_url'] = user_profile['profile_img_url']
    return { 
        'user': user_wanted_info
    }

def user_profile_setname_v2(token, name_first, name_last):
    """Summary
        Update the authorised user's first and last name
    Args:
        token (string): User session token
        name_first (string): String containing the user's desired new first name
        name_last (string): String containing the user's desired new last name
    
    Returns:
        Empty dictionary
    
    Raises:
        InputError: When name_first or name_last are not strings or not between 1 and 50 characters long
    """
    check_token(token)

    if type(name_first) != str:
        raise InputError("name_first is not of type string.")

    if type(name_last) != str:
        raise InputError("name_last is not of type string.")

    if not 1 <= len(name_first) <= 50:
        raise InputError("name_first is not between 1 and 50 characters inclusively in length.")

    if not 1 <= len(name_last) <= 50:
        raise InputError("name_last is not between 1 and 50 characters inclusively in length.")

    u_id = user_from_token(token)['u_id']
    for user in users:
        if user['u_id'] == u_id:
            user['name_first'] = name_first
            user['name_last'] = name_last
    return {}

def user_profile_setemail_v1(token, email):
    """Summary
        Update the authorised user's email address
    Args:
        token (string): User session token
        email (string): String containing the user's email
    
    Returns:
        Empty dictionary
    
    Raises:
        InputError: Email entered is not a valid email using the method provided here (unless you feel you have a better method).
        InputError: Email address is already being used by another user
    """
    check_token(token)
    u_id = user_from_token(token)['u_id']

    # InputError: Email entered is not a valid email using the method provided here (unless you feel you have a better method). 
    if not valid_email(email):
        raise InputError(f"Email entered {email} is not a valid email")

    # InputError: Email address is already being used by another user
    for user in users:
        if user['email'] == email:
            raise InputError(f"Email entered {email} is already being used by another user")
    
    # change the email information in the data user
    for user in users:
        if user['u_id'] == u_id:
            user['email'] = email
    return {}

def user_profile_sethandle_v1(token, handle_str):
    '''
    Summary:
        Update the authorised user's handle (i.e. display name)
    Args:
        token (string): A user session token 
        handle_str (string): The new proposed handle that the user wants to change to
    Returns: 
        a empty dictionary 

    Raises:
        InputError when:
            handle_str is not between 3 and 20 characters inclusive
            handle is already used by another user
    '''
    global users, channels, dms
    assert check_token(token)
    auth_user = user_from_token(token)
    if len(handle_str) < 3 or len(handle_str) > 20: 
        raise InputError("handle_str is not between 3 and 20 characters inclusive")
    if user_with_same_handle(handle_str): #check if another user has the same handle
        raise InputError("handle is already used by another user")
    auth_user['handle_str'] = handle_str
    return {
    }

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    """Summary
        Given the URL of a jpg image, crops the image within bounds 
        (x_start, y_start) and (x_end, y_end) and stores it locally to be accessed
        when displaying the user's profile photo.
    Args:
        token (string): A user session token
        img_url (string): A url to a jpg image
        x_start (int): The starting x coordinate of the image crop operation
        y_start (int): The starting y coordinate of the image crop operation
        x_end (int): The ending x coordinate of the image crop operation
        y_end (int): The ending y coordinate of the image crop operation
    
    Returns:
        Empty dictionary
    
    Raises:
        InputError: When the img_url parameter is invalid or returns a status code other than 
                    200, when img_url does not refer to a jpg image, when x_start and y_start
                    parameters are not less than their respective end parameters or when the
                    crop dimension parameters are not within the image dimensions.
        AccessError: When the token parameter is an invalid token
    """
    check_token(token)
    user = user_from_token(token)
    user_id = user['u_id']

    # Verify that img_url can be opened
    try:
        status_code = requests.get(img_url).status_code
    except requests.ConnectionError as ce: # Occurs if URL is not real or requests cannot connect for any reason
        raise InputError(f"Failed to connect to img_url {img_url}") from ce
    if status_code != 200: # Occurs if any error code is raised upon connecting to the URL
        raise InputError(f"img_url {img_url} returned an HTTP status code of {status_code} (expected 200)")

    img_info = imgspy.info(img_url)

    # Check whether file is a jpg image
    if not img_info['type'] == 'jpg':
        raise InputError(f"File is not a jpg image (got {img_info['type']}).")

    # Check whether start coords are less than end coords
    if not (x_start < x_end and y_start < y_end):
        raise InputError(f"x_start and y_start parameters (got {x_start}, {y_start}) must be smaller than x_end and y_end parameters (got {x_end}, {y_end})")

    #Check whether coordinates are within the bounds of the image
    if not (x_start >= 0 and x_end <= img_info['width'] and y_start >= 0 and y_end <= img_info['height']):
        raise InputError(f"Crop dimensions ({x_start}, {y_start}, {x_end}, {y_end}) not within the dimensions of the image at the URL ({img_info['width']}x{img_info['height']}).")

    time_stamp = current_unix_timestamp()
    img_path = f'static/profile_photos/{user_id}-{time_stamp}.jpg' # Local path to save image to
    urllib.request.urlretrieve(img_url, img_path) # Retrieve image from URL and save it to path

    imageObject = Image.open(img_path) # Open image in PIL

    cropped_img = imageObject.crop((x_start, y_start, x_end, y_end)) # Crop image to desired dimensions
    cropped_img.save(img_path) # Overwrite uncropped image at original path

    # Delete old profile image if it is not the default image
    prev_profile_img = user['profile_img_url'].replace(url,'') # Remove url from profile_img_url to get image path
    if prev_profile_img != f'static/profile_photos/default.jpg':
        os.remove(prev_profile_img)

    user['profile_img_url'] = url + img_path

    return {}

def user_stats_v1(token):
    """Summary
        Fetches a user's Dreams usage statistics
    Args:
        token (string): A user session token
    
    Returns:
        stats_dict: Dictionary of the form:
                    {
                        channels_joined: [{num_channels_joined, time_stamp}],
                        dms_joined: [{num_dms_joined, time_stamp}], 
                        messages_sent: [{num_messages_sent, time_stamp}], 
                        involvement_rate 
                    }
    Raises:
        AccessError: When the token parameter is an invalid token
    """
    check_token(token)

    '''
    Dictionary of shape {
    channels_joined: [{num_channels_joined, time_stamp}],
    dms_joined: [{num_dms_joined, time_stamp}], 
    messages_sent: [{num_messages_sent, time_stamp}], 
    involvement_rate 
    }
    '''
    # sum(num_channels_joined, num_dms_joined, num_msgs_sent)/sum(num_dreams_channels, num_dreams_dms, num_dreams_msgs)
    user = user_from_token(token)

    stats_dict = user['stats'].copy()

    ch_joined_list = stats_dict['channels_joined']
    dm_joined_list = stats_dict['dms_joined']
    msg_sent_list = stats_dict['messages_sent']

    ch_joined = 0
    if len(ch_joined_list) > 0:
        ch_joined = ch_joined_list[-1]['num_channels_joined']

    dm_joined = 0
    if len(dm_joined_list) > 0:
        dm_joined = dm_joined_list[-1]['num_dms_joined']

    msg_sent = 0
    if len(msg_sent_list) > 0:
        msg_sent = msg_sent_list[-1]['num_messages_sent']

    total_channels = len(channels)
    total_dms = len(dms)
    total_messages = len(messages)

    totals = total_channels + total_dms + total_messages
    
    inv_rate = 0
    if totals > 0:
        inv_rate = (ch_joined + dm_joined + msg_sent) / totals

    stats_dict['involvement_rate'] = inv_rate

    return { 'user_stats' : stats_dict }
