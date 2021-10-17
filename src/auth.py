import re

from src.data import users, tokens, next_u_id, notifications, reset_codes
from src.error import InputError
from src.helpers import check_token, user_from_token, valid_email, generate_token, get_hash, random_code_generator
from src.config import url

def auth_login_v2(email, password):
    """Summary
        Given a registered user's email and password, returns a new session token and their user id
    Args:
        email (string): An email address
        password (string): A password
    
    Returns:
        Dictionary: Contains the user's token and user id
    
    Raises:
        InputError: When an invalid email is given, the given password is incorrect, or the email entered does not
                    match any registered user's email
    """
    global tokens
    if not valid_email(email):
        raise InputError(f"Email {email} is not a valid email")

    for user in users:
        if user['email'] == email and user['permission'] != 0:# Check for email match to valid, non-removed user
            if user['password'] == get_hash(password): # Compare stored password hash to hashed password input
                auth_user_id = user['u_id']
                token = generate_token(auth_user_id)
                return { 'token' : token, 'auth_user_id' : auth_user_id }
            else:
                raise InputError(f"Password {password} is not correct")

    raise InputError(f"Email {email} does not belong to a user.")

def auth_register_v2(email, password, name_first, name_last):  
    '''
    <this function will take in a users first name, last name, their email and a password and create a new account "auth_user_id" and generate a handle>

    Arguments:
        <email>      (<string>)     - <this is the email of the new user>
        <password>   (<string>)     - <this is the password of the new user>
        <name_first> (<string>)     - <this is the first name of the new user>
        <name_last>  (<string>)     - <this is the last name of the new user>

    Exceptions:
        InputError  - Occurs when email entered is not a valid email using the method provided here
        InputError  - Occurs when email address is already being used by another user
        InputError  - Occurs when password entered is less than 6 characters long
        InputError  - Occurs when first name is not between 1 and 50 characters inclusively in length
        InputError  - Occurs when last name is not between 1 and 50 characters inclusively in length

    Return Value:
        Returns <{ token, auth_user_id }>       on <when new user is successfully registered, return the token and the id of this new user>
    '''

    global users, next_u_id, tokens, notifications

    #     Email entered is not a valid email using the method provided here (unless you feel you have a better method).
    if not valid_email(email):
        raise InputError(f"{email} address is an invaild email")

    #     Email address is already being used by another user, and the other user is not removed
    for user in users:
        if email == user["email"] and user["permission"] != 0:
            raise InputError(f"{email} address has already been used")

    #     Password entered is less than 6 characters long
    if len(password) < 6:
        raise InputError(f"Password entered: {password} is less than 6 characters long")

    #     name_first is not between 1 and 50 characters inclusively in length
    #     name_last is not between 1 and 50 characters inclusively in length
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(f"The first name entered: {name_first} is not between 1 and 50 characters inclusively in length")
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(f"The last name entered: {name_last} is not between 1 and 50 characters inclusively in length")
    

    handle = set_handle(name_first + name_last)
    handle_time = -1

    # repeat handle
    for user in users:
        if handle == user["handle_real"]:
            handle_time += 1
    
    # add number if too long
    if handle_time != -1:
        handle_show = "{}{}".format(handle, handle_time)
    else:
        handle_show = handle

    # id
    user_id = next_u_id['id']
    next_u_id['id'] += 1

    new_user = {
        'u_id': user_id,
        'email': email,
        'password' : get_hash(password),
        'name_first': name_first,
        'name_last': name_last,
        'handle_times': handle_time,
        'handle_real': handle,
        'handle_str': handle_show,
        'channels' : [],
        'permission' : 1 if user_id == 0 else 2, # First user to register is a Dreams owner
        'dms' : [],
        'profile_img_url' : url + 'static/profile_photos/default.jpg',
        'stats' : { 'channels_joined' : [],'dms_joined' : [],'messages_sent' : [] }
    }

    # Create notification list for new user
    new_noti_list = {'u_id' : user_id, 'notifications' : []}
    notifications.append(new_noti_list)

    token = generate_token(new_user['u_id'])
    users.append(new_user)

    return { 'token' : token , 'auth_user_id' : new_user['u_id'] }

# delete the "@" and " " to create a handle
def set_handle(name):

    new = ""
    name = name.lower()
    for i in range(len(name)):
        if name[i] != ' ' and name[i] != '@':
            new += name[i]
            
    if len(new) > 20:
        new = new[:20]
    
    return new

def auth_logout_v1(token):
    '''
    <Given an active token, invalidates the token to log the user out. If a valid token is given, and the user is successfully logged out, it returns true, otherwise false.>

    Arguments:
        <token>      (<string>)     - <a string which store the information of the user>

    Exceptions:
        no exception in this function

    Return Value:
        Returns <{ is_success }>       on <when new user tried to logout, return if successed logout>
    '''
    global tokens
    check_token(token)
    # Remove all of the user's current tokens
    # Must be done this way to ensure that tokens list is updated across all modules
    cleared_tokens = [tkn for tkn in tokens if tkn != token]
    tokens.clear()
    for tkn in cleared_tokens:
        tokens.append(tkn)
    return { 'is_success' : True }

def auth_passwordreset_request_v1(email):
    '''
    Summary:
        Given an email address, if the user is a registered user, 
        sends them an email containing a specific secret code, that when entered in auth_passwordreset_reset, 
        shows that the user trying to reset the password is the one who got sent this email.
    Args:
        email (string): email
    Returns: 
        empty dictionary
    Raises:
        Raises no errors
    '''
    global reset_codes
    
    #registered_user = False
    for user in users:
        if user['email'] == email and user['permission'] != 0:
            #registered_user = True
            code_data = {}
            code_data['email'] = email
            code_data['u_id'] = user['u_id']
            code_data['code'] = random_code_generator()
            code_data['name'] = user['name_first']
            reset_codes.append(code_data)
            return {}
    
    #if registered_user == False:
        #raise InputError(f"user with email {email} has not registered") # this was not included 
    return {}

#i noticed playing with the front end that this will only apply after password request has gone through "there are layers" so we dont have to validate if there is a user because they can only get to the part of changing their password if there email is valid and that confirms them to be valid
def auth_passwordreset_reset_v1(reset_code, new_password):
    '''
    Summary:
        Given a reset code for a user, set that user's new password to the password provided
    Args:
        reset_code (string): A string of numbers and captial letters
        password (string): The password that the user wants to change theirs to
    Returns: 
        empty dictionary
    Raises:
        InputError when:
            reset_code is not a valid reset code
            Password entered is less than 6 characters long
    '''
    global users, reset_codes
    if len(new_password) < 6:
        raise InputError("Password entered is less than 6 characters long")
    
    for code_data in list(reset_codes): #ask team i delete the code after because we dont need it anymore i need list() here right
        if code_data['code'] == reset_code:
            for user in users:
                if code_data['u_id'] == user['u_id']: #i can add email here as well to double check, u_id i unique though,should be fine 
                    user['password'] = get_hash(new_password)
                    reset_codes.remove(code_data) #delete after because dont need anymore? added list() here right
                    return {}
              
    # If loop exits without returning, code is invalid            
    raise InputError("reset_code is not a valid reset code")
