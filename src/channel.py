from src.data import users, channels, messages
from src.error import InputError, AccessError
from src.helpers import check_token, valid_channel, user_from_token,is_channel_member, is_channel_owner, valid_user, find_channel, user_from_id, send_channel_added_notification, update_user_channel_stats, is_dreams_owner


def channel_invite_v2(token, channel_id, u_id):
    '''
    Summary:
        Invites a user (with user id u_id) to join a channel with ID channel_id. 
        Once invited the user is added to the channel immediately.
    Args:
        token (string): A user session token 
        channel_id (int): A channel_id number
        u_id (int): A user id 
    Returns: 
        empty dictionary

    Raises:
        InputError when:
            channel_id does not refer to a valid channel
            u_id does not refer to a valid user
        AccessError when:
            the authorised user is not already a member of the channel
    '''
    global users, channels 
    assert check_token(token)
    auth_user = user_from_token(token)

    if valid_channel(channel_id) == False: 
        raise InputError(f"Channel ID {channel_id} is not a valid channel")

    if valid_user(u_id) == False: 
        raise InputError(f"u_id {u_id} does not refer to a valid user")

    current_channel = find_channel(channel_id) #current channel with the given channel id
    invitee = user_from_id(u_id)

    if auth_user['u_id'] not in current_channel['all_members']:
        raise AccessError(f"Authorised user {auth_user['u_id']} is not a member of channel with channel_id {channel_id}")
    
    if u_id in current_channel['all_members']:
        raise AccessError(f"u_id {u_id} you are inviting is already inside the channel")
                
    current_channel['all_members'].append(u_id)
    if invitee['permission'] == 1: # Dreams owner is automatically channel owner
        current_channel['owner_members'].append(u_id)
    invitee['channels'].append(channel_id)
    update_user_channel_stats(invitee['u_id'])
    send_channel_added_notification(auth_user['handle_str'], u_id, current_channel['channel_id'])
    return {}

def channel_details_v2(token, channel_id):
    '''
    Summary:
        Given a Channel with ID channel_id that the authorised user is part of, 
        provide basic details about the channel
    Args:
        token (string): A user session token 
        channel_id (int): A channel_id number
    Returns: 
        a dictionary which contains:
            name of the channel 
            the is_public status of the channel (True for public, False for private)
            a list of owner_member for the channel 
            a list of members for a channel
    Raises:
        InputError when:
            Channel ID is not a valid channel
        AccessError when:
            Authorised user is not a member of channel with channel_id
    '''
    global users, channels
    assert check_token(token)
    auth_user = user_from_token(token)

    if valid_channel(channel_id) == False: 
        raise InputError(f"Channel ID {channel_id} is not a valid channel")

    current_channel = find_channel(channel_id) #current channel with the given channel id
    
    if auth_user['u_id'] not in current_channel['all_members']:
        raise AccessError(f"Authorised user {auth_user['u_id']} is not a member of channel with channel_id {channel_id}")
                
    owner_members = []
    all_members = []
    for u_id in current_channel['all_members']:
        for user in users:
            if user['u_id'] == u_id:
                user_details = {}
                user_details['u_id'] = user['u_id']
                user_details['email'] = user['email']
                user_details['name_first'] = user['name_first']
                user_details['name_last']= user['name_last']
                user_details['handle_str'] = user['handle_str']
                user_details['profile_img_url'] = user['profile_img_url']
                all_members.append(user_details)
                if u_id in current_channel['owner_members']:
                    owner_members.append(user_details)
    return { #give the name of the dictonary then the values
        'name': current_channel['name'],
        'is_public': current_channel['is_public'],
        'owner_members': owner_members, 
        'all_members': all_members 
    }

def channel_messages_v2(token, channel_id, start):
    """Summary
        Given a Channel with ID channel_id that the authorised user is part of, return up to 50 messages between 
        index "start" and "start + 50". Message with index 0 is the most recent message in the channel. This 
        function returns a new index "end" which is the value of "start + 50", or, if this function has returned 
        the least recent messages in the channel, returns -1 in "end" to indicate there are no more messages to 
        load after this return.
    Args:
        token (string): A user session token
        channel_id (int): A channel id number
        start (int): The index in the channel's list of messages at which to begin collecting them
    
    Returns:
        Dictionary: Contains the start index, the end index (-1 if the final message in the list was collected,
                    or start + 50 if 50 messages were collected without reaching the end of the list) and the
                    list of collected messages.
    
    Raises:
        AccessError: When an invalid token is given, or authorised user is not a member of channel with channel_id
        InputError: When channel_id does not refer to a valid channel or start is negative or greater than the 
        total number of messages in the channel 
    """
    check_token(token)
    auth_user_id = user_from_token(token)['u_id']

    # Retrieve messages from channel with given channel_id 
    message_ids = None
    for channel in channels:
        if channel['channel_id'] == channel_id:
            if auth_user_id in channel['all_members']:
                message_ids = channel['messages']
            else:
                raise AccessError(f"Authorised user is not a member of channel with id {channel_id}")
    if message_ids == None: # If list is still None, channel has not been found
        raise InputError(f"channel id {channel_id} does not refer to a valid channel")

    # Collect all messages in the target channel
    messageList = []
    for message in messages:
        if message['message_id'] in message_ids:
            messageList.append(message)
   
    # If the channel has no messages and start = 0, return an empty list with end = -1
    if start == 0 and not len(messageList):
        return { 'messages' : messageList, 'start' : start, 'end' : -1 }

    # Check whether start index is negative
    if start < 0:
        raise InputError(f"start index cannot be negative (given {start})")
    
    messageList.reverse() # Most recent message should have index 0
    
    # Collect up to 50 messages from the channel's messages
    if start < len(messageList): # Check whether start index is within bounds of message list
        output = []
        index = start
        while len(output) < 50:
            if index >= len(messageList): # Index exceeds list size, max. number of messages have been collected
                return { 'messages' : output, 'start' : start, 'end' : -1 }
            message = messageList[index]

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
        # If loop finishes, 50 messages have been collected
        # Set end to -1 if channel had exactly 50 messages from start index, or start + 50 otherwise
        return { 'messages' : output, 'start' : start, 'end' : start + 50 if len(messageList) > start + 50 else -1}
    else:
        raise InputError(f"start index {start} is greater than the total number of messages in the channel {len(messages)}")

def channel_leave_v1(token, channel_id):
    '''
    <Given a channel ID, the user removed as a member of this channel. Their messages should remain in the channel>

    Arguments:
        <token> (<string>)    - <the user that is trying to leave from the channel>
        <channel_id> (<integer>)    - <the channel that the user is trying to leave>

    Exceptions:
        InputError  - Occurs when Channel ID is not a valid channel
        AccessError  - Occurs when Authorised user is not a member of channel with channel_id

    Return Value:
        no returns in this function
    '''
    
    check_token(token)

    # Channel ID is not a valid channel
    if not valid_channel(channel_id):
        raise InputError(f"Channel ID {channel_id} is not a valid channel")
    '''
    user = user_from_token(token)
    u_id = user['u_id']
    # Authorised user is not a member of channel with channel_id
    if not is_channel_member(u_id, channel_id):
        raise AccessError(f"Authorised user {u_id} is not a member of channel with channel_id")
    '''
  

    auth_user = user_from_token(token)
    if is_channel_member(auth_user['u_id'], channel_id) == False:
        raise AccessError(f"Authorised user {auth_user['u_id']} is not a member of channel with channel_id")
    
    for channel in channels: 
        if channel['channel_id'] == channel_id:
            channel['all_members'].remove(auth_user['u_id'])
            for owner_member in list(channel['owner_members']):
                if owner_member == auth_user['u_id']:
                    channel['owner_members'].remove(auth_user['u_id'])
    
    auth_user['channels'].remove(channel_id)
    update_user_channel_stats(auth_user['u_id'])
    
    '''
    # remove the member from the channel all_member list
    record = -1
    for channel in channels:
        if channel['channel_id'] == channel_id:
            members = channel['all_members']
            for i in range(len(members)):
                if members[i] == u_id:
                    record = i
    
    if record != -1:
        members.remove(record)
    
    # remove this channel in the user's channels
    # record is the channel which need to be deleted 
    record = -1
    user_channel = user['channels']
    for i in range(len(user_channel)):
        if user_channel[i] == channel_id:
            record = i

    # removed the record 
    if record != -1:
        user_channel.remove(record)
    '''
    return {
    }

def channel_join_v2(token, channel_id):
    '''
    Summary:
        Given a channel_id of a channel that the authorised user can join, 
        add them to that channel members
    Args:
        token (string): A user session token 
        channel_id (int): A channel_id number
    Returns: 
        a empty dictionary
    Raises:
        InputError when:
            Channel ID is not a valid channel
        AccessError when:
            channel_id refers to a channel that is private 
            (when the authorised user is not a global owner)
    '''
    global users, channels
    assert check_token(token)
    auth_user = user_from_token(token)
    
    if valid_channel(channel_id) == False: 
        raise InputError(f"Channel ID {channel_id} is not a valid channel")
    current_channel = find_channel(channel_id) #current channel with the given channel id

    is_dreams_owner = auth_user['permission'] == 1

    not_in_current_channel = auth_user['u_id'] not in current_channel['all_members']

    if current_channel['is_public'] == True:
        if not_in_current_channel:
            if is_dreams_owner:
                current_channel['owner_members'].append(auth_user['u_id'])
            current_channel['all_members'].append(auth_user['u_id'])
            auth_user['channels'].append(channel_id)
            update_user_channel_stats(auth_user['u_id'])
    else: 
        if is_dreams_owner and not_in_current_channel:
            current_channel['owner_members'].append(auth_user['u_id'])
            current_channel['all_members'].append(auth_user['u_id'])
            auth_user['channels'].append(channel_id)
            update_user_channel_stats(auth_user['u_id'])
        else: 
            raise AccessError(f"channel_id {channel_id} refers to a channel that is private ( authorised user is not a global owner)")

    return {}

def channel_addowner_v1(token, channel_id, u_id):
    '''
    Summary:
        Make user with user id u_id an owner of this channel
    Args:
        token (string): A user session token 
        channel_id (int): A channel_id number
        u_id (int): A user id number
    Returns: 
        a empty dictionary
    Raises:
        InputError when:
            Channel ID is not a valid channel
            When user with user id u_id is already an owner of the channel
        AccessError when:
           the authorised user is not an owner of the **Dreams**, 
           or an owner of this channel
    '''
    global users, channels
    assert check_token(token)
    assert valid_user(u_id)
    if valid_channel(channel_id) == False: 
        raise InputError(f"Channel ID is not a valid channel")
    auth_user = user_from_token(token)
    current_channel = find_channel(channel_id) #current channel with the given channel id
    
    if not is_channel_owner(auth_user['u_id'], channel_id) and not is_dreams_owner(auth_user['u_id']): 
        raise AccessError(f"the authorised user is not an owner of the channel or Dreams")
    if is_channel_owner(u_id, channel_id) == True: 
        raise InputError(f"User with user id {u_id} is already an owner of the channel")

    target_user = user_from_id(u_id)

    current_channel['owner_members'].append(u_id) 
    if u_id not in current_channel['all_members']:
        current_channel['all_members'].append(u_id)
        target_user['channels'].append(channel_id)
        update_user_channel_stats(u_id)
        send_channel_added_notification(auth_user['handle_str'], u_id, current_channel['channel_id'])
    return {}

def channel_removeowner_v1(token, channel_id, u_id):
    """Summary
        Remove user with user id u_id from the owner members list of channel with channel id channel_id
    Args:
        token (string): A user session token
        channel_id (int): A channel id number
        u_id (int): A user id number

    Returns:
        Empty dictionary
    
    Raises:
        AccessError: When an invalid token is given, or the user referred to by token is not a Dreams owner
                     or an owner of the channel with channel id channel_id
        InputError: When channel_id does not refer to a valid channel, when the user with user id u_id is
                    not an owner of the channel, or the user with user id u_id is currently the only owner
    """
    check_token(token)

    auth_user = user_from_token(token)
    # User is a Dreams owner if their permission code is 1
    auth_user_is_dreams_owner = auth_user['permission'] == 1

    for channel in channels:
        if channel['channel_id'] == channel_id:
            owners = channel['owner_members']
            # Verify that auth user is a Dreams owner or an owner of the channel 
            if auth_user_is_dreams_owner or auth_user['u_id'] in owners:
                # Verify that user to be removed is an owner
                if u_id in owners:
                    # Verify that there is more than one channel owner
                    if len(owners) > 1:
                        channel['owner_members'].remove(u_id)
                        return {}
                    else:
                        raise InputError(f"User with user id {u_id} is currently the only owner")
                else:
                    raise InputError(f"User with user id {u_id} is not an owner of the channel")
            else:
                raise AccessError(f"Authorised user {auth_user['handle_str']} is not an owner of the **Dreams**, or an owner of this channel")

    raise InputError(f"Channel ID {channel_id} does not refer to a valid channel")
