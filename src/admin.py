from src.data import users, channels, messages, tokens, dms
from src.error import InputError, AccessError
from src.helpers import check_token, user_from_token, valid_user, find_all_dream_owners, user_from_id

def admin_userpermission_change_v1(token, u_id, permission_id):
    """Summary
        Enables a Dreams owner to change the permissions of another user between Dreams owner (1) and
        standard user (2).
    Args:
        token (string): User session token
        u_id (integer): User id number
        permission_id (integer): Either 1, indicating Dreams owner, or 2, indicating standard user
    
    Returns:
        Empty dictionary
    
    Raises:
        AccessError: When an invalid token value is given, or when the user associated with the token
                     is not a Dreams owner
        InputError: When permission_id does not refer to a valid permission, or 
                    u_id does not refer to a valid user
    """
    check_token(token) # Check for invalid token

    if user_from_token(token)['permission'] != 1:
        raise AccessError("Authorised user is not an owner.")

    if not 1 <= permission_id <= 2: # Check for invalid permission_id
        raise InputError("permission_id does not refer to a valid permission.")

    # Search for user with user id u_id and change their permission if found
    for user in users:
        if user['u_id'] == u_id:
            user['permission'] = permission_id
            return {}
    raise InputError("u_id does not refer to a valid user.")

def admin_user_remove_v1(token, u_id): 
    '''
    Summary:
        Given a User by their user ID, remove the user from the Dreams. 
        Dreams owners can remove other **Dreams** owners (including the original first owner). 
        Once users are removed from **Dreams**, the contents of the messages they sent will be replaced by 'Removed user'. 
        Their profile must still be retrievable with user/profile/v2, with their name replaced by 'Removed user'.
    Args:
        token (string): A user session token 
        u_id (int): A user id number
    Returns: 
        empty dictionary
    Raises:
        InputError when:
            u_id does not refer to a valid user
            The user is currently the only owner
        AccessError when:
            The authorised user is not an owner
    '''
    global users, channels, tokens, dms
    assert check_token(token)
    auth_user = user_from_token(token)
    if valid_user(u_id) == False: 
        raise InputError(f"User with u_id is not a valid user")
    dream_owners = find_all_dream_owners() #list of all dream owners
    if auth_user['permission'] != 1:
        raise AccessError("The authorised user is not an owner")
    elif auth_user['u_id'] == u_id and len(dream_owners) == 1:
        # Only way that user being removed can be only owner is if they are removing themself
        raise InputError("The user is currently the only owner")
    
    # Remove all tokens associated with user being removed
    cleared_tokens = [tkn for tkn in tokens if user_from_token(tkn)['u_id'] != u_id]
    tokens.clear()
    for tkn in cleared_tokens:
        tokens.append(tkn)

    user = user_from_id(u_id)
    user['name_first'] = 'Removed'
    user['name_last'] = 'user'
    user['permission'] = 0 # User permission id 0 indicates a removed user
    
    for channel in channels:
        for owner_member in channel['owner_members']:
            if owner_member == u_id:
                channel['owner_members'].remove(u_id)
        for normal_member in channel['all_members']:
            if normal_member == u_id:
                channel['all_members'].remove(u_id)
                
    for dm in dms:
        for member in dm['members']:
            if member == u_id:
                dm['members'].remove(u_id)

    for message in messages: 
        if message['author_id'] == u_id:
            message['message'] = 'Removed user'

    return {
    }
