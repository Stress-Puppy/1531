from src.data import users, messages, channels, next_dm_id, dms
from src.error import InputError, AccessError
from src.helpers import check_token, user_from_token, user_from_id, is_dm_member, find_dm, valid_dm, valid_user, join_handle, send_dm_added_notification, update_dm_stats, update_user_dm_stats

def dm_messages_v1(token, dm_id, start):
    """Summary
        Given a DM with ID dm_id that the authorised user is part of, return up to 50 messages between index 
        "start" and "start + 50". Message with index 0 is the most recent message in the channel. This function 
        returns a new index "end" which is the value of "start + 50", or, if this function has returned the least 
        recent messages in the channel, returns -1 in "end" to indicate there are no more messages to load after 
        this return.
    Args:
        token (string): A user session token
        dm_id (int): A dm id number
        start (int): The index in the dm's list of messages at which to begin collecting them
    
    Returns:
        TYPE: Contains the start index, the end index (-1 if the final message in the list was collected,
              or start + 50 if 50 messages were collected without reaching the end of the list) and the
              list of collected messages.
    
    Raises:
        AccessError: When an invalid token is given, or authorised user is not a member of channel with channel_id
        InputError: When dm_id does not refer to a valid dm or start is negative or greater than the 
        total number of messages in the channel 
    """
    check_token(token)
    auth_user_id = user_from_token(token)['u_id']

    # Retrieve messages from channel with given channel_id 
    message_ids = None
    for dm in dms:
        if dm['dm_id'] == dm_id:
            if auth_user_id in dm['members']:
                message_ids = dm['messages']
            else:
                raise AccessError(f"Authorised user is not a member of dm with id {dm_id}")
    if message_ids == None:
        raise InputError(f"dm id {dm_id} does not refer to a valid dm")
   
    messageList = []
    for message in messages:
        if message['message_id'] in message_ids:
            messageList.append(message)

    # If the channel has no messages, return an empty list
    if start == 0 and not len(messageList):
        return { 'messages' : messageList, 'start' : start, 'end' : -1 }

    # Check whether start index is negative
    if start < 0:
        raise InputError(f"start cannot be negative (given {start})")

    messageList.reverse() # Most recent message should have index 0
    
    # Check whether start index is within bounds of message list
    if start < len(messageList):
        output = []
        index = start
        while len(output) < 50:
            if index >= len(messageList):
                return { 'messages' : output, 'start' : start, 'end' : -1 }
            message = messageList[index]

            # { react_id, u_ids, is_this_user_reacted } 

            react_dict = { 'react_id' : 1,
                           'u_ids' : message['reacts'],
                           'is_this_user_reacted' : auth_user_id in message['reacts'] }

            message_dict = {}
            message_dict['message_id'] = message['message_id']
            message_dict['u_id'] = message['author_id']
            message_dict['message'] = message['message']
            message_dict['time_created'] = message['time_created']
            message_dict['reacts'] = [react_dict]
            message_dict['is_pinned'] = message['is_pinned']
            
            output.append(message_dict)
            index += 1

        return { 'messages' : output, 'start' : start, 'end' : start + 50 if len(messageList) > 50 else -1 }
    else:
        raise InputError(f"start index {start} is greater than the total number of messages in the channel {len(messages)}")

def dm_invite_v1(token, dm_id, u_id):
    """Summary
        Inviting a user to an existing dm
    Args:
        token (string): A user session token
        dm_id (int): A dm id number
        u_id (int): An user's id, who want to add this dm
        
    Returns:
        Empty dictionary
    
    Raises:
        AccessError: When an invalid token is given, or the user that token refers to is not the creator of the dm
                     with id dm_id
    """
    check_token(token)
    auth_user = user_from_token(token)

    invitee = user_from_id(u_id)

    # InputError: When u_id does not refer to a valid user.
    if invitee == {}:
        raise InputError(f"id {u_id} does not refer to a valid user")

    # search all the dm in dms, and search the current dm by dm_id
    for dm in dms:
        if dm['dm_id'] == dm_id:
            # if auth user is a member of the dm, add the u_id to this dm
            if auth_user['u_id'] in dm['members']:
                dm['members'].append(u_id)
                invitee['dms'].append(dm_id)
                update_user_dm_stats(invitee['u_id'])
                send_dm_added_notification(auth_user['handle_str'], u_id, dm['dm_id'])
                return {}
            else:
                raise AccessError(f"The authorised user {auth_user['handle_str']} is not already a member of the DM with id {dm_id}")

    # InputError: When dm_id does not refer to a valid dm
    raise InputError(f"id {dm_id} does not refer to a valid dm")
    
def dm_remove_v1(token, dm_id):
    """
    Summary
        Delete an existing DM. This can only be done by the original creator of the DM.
    Args:
        token (string): A user session token
        dm_id (int): A dm id number

        AccessError: When an invalid token is given, or the authorised user is not already a member of the DM
        InputError: When dm_id does not refer to a valid dm, 
        InputError: When u_id does not refer to a valid user.
    """
    global messages
    check_token(token)
    auth_user = user_from_token(token)
      
    # Check that auth user is the creator of the dm  
    dm_found = False
    dm_members = []   
    for dm in dms:
        if dm['dm_id'] == dm_id:
            dm_found = True
            dm_members = dm['members']
            if dm['creator'] != auth_user['u_id']:
                raise AccessError(f"User {auth_user['handle_str']} is not the creator of dm with id {dm_id}")
    if not dm_found:
        raise InputError(f"id {dm_id} does not refer to a valid dm")

    # Remove dm from all members' dm list
    for user in users:
        if user['u_id'] in dm_members:
            user['dms'].remove(dm_id)
            update_user_dm_stats(user['u_id'])

    # Delete messages sent in this dm
    for message in list(messages):
        if message['dm_id'] == dm_id:
            messages.remove(message)

    # Remove desired dm from dms list
    # Must be done this way to ensure that dms list is updated across all modules
    cleared_dms = [dm for dm in dms if dm['dm_id'] != dm_id]
    dms.clear()
    for dm in cleared_dms:
        dms.append(dm)

    update_dm_stats()

    return {}
                     
def dm_details_v1(token, dm_id):
    """Summary
        Allows users that are members of a direct message to view basic information about the DM
        
        Dictionary: Contains the name of the dm and details about each of its members
    
    Raises:
        AccessError: When an invalid token is given, or the authorised user referred to by the token is not
                     a member of the dm
    
        InputError: When dm_id does not refer to a valid dm
    """
    check_token(token)
    auth_user = user_from_token(token)
    
    # Find the desired dm, if it exists, and retrieve its name and list of member u_ids
    output = None
    for dm in dms:
        if dm['dm_id'] == dm_id:
            if auth_user['u_id'] in dm['members']:
                output = { 'name' : dm['name'], 'members' : [] }
                member_ids = dm['members']
            else:
                raise AccessError(f"Authorised user {auth_user['handle_str']} is not a member of DM with id {dm_id}")
    
    if output == None: # If output is still None, DM with id dm_id was not found
        raise InputError(f"DM id {dm_id} does not refer to a valid DM")
    
    # Find all dm members, and append their details to output
    for user in users:
        if user['u_id'] in member_ids:
            member_details = { 'u_id' : user['u_id'],
                               'email' : user['email'],
                               'name_first' : user['name_first'],
                               'name_last' : user['name_last'],
                               'handle_str' : user['handle_str'],
                               'profile_img_url' : user['profile_img_url'] }
            output['members'].append(member_details)

    return output

def dm_leave_v1(token, dm_id):
    '''
    Summary:
        Given a DM ID, the user is removed as a member of this DM
    Args:
        token (string): A user session token 
        dm_id (int): A dm_id number
    Returns: 
        a empty dictionary
    Raises:
        InputError when:
            dm_id is not a valid DM
        AccessError when:
            Authorised user is not a member of DM with dm_id
    '''
    global users, channels, dms
    assert check_token(token)
    
    auth_user = user_from_token(token)
    if valid_dm(dm_id) == False:
        raise InputError(f"dm_id is not a valid DM")
        
    current_dm = find_dm(dm_id) #find the current dm 

    if auth_user['u_id'] not in current_dm['members']:
        raise AccessError(f"Authorised user is not a member of DM with dm_id")

    # Remove dm from user's list of dms
    auth_user['dms'].remove(dm_id)
    update_user_dm_stats(auth_user['u_id'])

    # Remove user from dm's members list
    current_dm['members'].remove(auth_user['u_id'])
            
    return {}

def dm_create_v1(token, u_id):
    '''
    Summary:
        u_ids is the user(s) that this DM is directed to, and will not include the creator. 
        The creator is the owner of the DM. 
        
        name should be automatically generated based on the user(s) that is in this dm. 
        The name should be an alphabetically-sorted, comma-separated list of user handles, e.g. 
        'handle1, handle2, handle3'.
    Args:
        token (string): A user session token 
        u_ids (list): A list of user ids 
    Returns: 
        a dictionary which contains the id of the dm (dm_id) 
        and the name of the dm which is the concatenated handles

    Raises:
        InputError when:
            u_id does not refer to a valid user
    '''
    global users, channels, next_dm_id, dms
    assert check_token(token)
    
    auth_user = user_from_token(token)
    user_list_handles = [auth_user['handle_str']]
    
    for i in range(len(u_id)):
        if valid_user(u_id[i]) == False: 
            raise InputError(f"u_id {u_id[i]} does not refer to a valid user")
        else: 
            member = user_from_id(u_id[i])
            user_list_handles.append(member['handle_str'])  
    name = join_handle(user_list_handles)
    dm_id = next_dm_id['id'] #give the current global id number to this dm
    next_dm_id['id'] += 1 #after add one so the the dm id is always unique 
    dm_members = [auth_user['u_id']]
    for user_id in u_id:
        dm_members.append(user_id)

    # Add dm to each member's list of dms
    for user in users:
        if user['u_id'] in dm_members:
            user['dms'].append(dm_id)
            update_user_dm_stats(user['u_id'])
        
    new_dm = {
        'dm_id' : dm_id,
        'name' : name,
        'creator' : auth_user['u_id'],
        'messages': [],
        'members' : dm_members 
    }
    
    dms.append(new_dm)

    update_dm_stats()

    for user_id in new_dm['members']:
        send_dm_added_notification(auth_user['handle_str'], user_id, dm_id)
    
    return {
        'dm_id': dm_id,
        'dm_name': new_dm['name']
    }

def dm_list_v1(token):
    """Summary
        Returns the list of DMs that the user is a member of
    Args:
        token (string): A user session token
    
    Returns:
        Dictionary: { dms } ({dm_id，name})  Contains the id and name of the dm
    
    Raises:
        AccessError: invaild token

    """
    check_token(token)
    auth_user = user_from_token(token)

    # Find the desired dm, if it exists, and return all dm's name and id
    output = []
    for dm in dms:
        if auth_user['u_id'] in dm['members']:
            id_name = { 'dm_id' : dm['dm_id'], 'name' : dm['name']}
            output.append(id_name)
    
    return { 'dms' : output }
