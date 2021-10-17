import threading
import time

from src.data import users, next_message_id, messages, channels, dms, tokens, future_messages
from src.standup import standup_send_v1, standup_start_v1
from src.error import InputError, AccessError
from src.helpers import check_token, user_from_token, is_dreams_owner, is_channel_owner, is_channel_member, is_dm_member, valid_channel, find_channel, current_unix_timestamp, get_message_from_message_id, find_dm, user_from_id, send_dm_tag_notification, send_channel_tag_notification, update_message_stats, update_user_message_stats, valid_dm, valid_message, send_channel_message_react_notification, send_dm_message_react_notification

def message_send_v2(token, channel_id, message):
    '''
    Summary:
        Send a message from authorised_user to the channel specified by channel_id. 
        Note: Each message should have it's own unique ID. 
        I.E. No messages should share an ID with another message, 
        even if that other message is in a different channel.
    Args:
        token (string): A user session token 
        channel_id (int): A channel_id number
        message (string): a message string 
    Returns: 
        empty dictionary which contains the message_id
    Raises:
        InputError when:
            Message is more than 1000 characters
        AccessError when:
            the authorised user has not joined the channel they are trying to post to
    '''
    global users, channels, next_message_id, messages
    assert check_token(token)
    assert valid_channel(channel_id)
    
    auth_user = user_from_token(token)
    current_channel = find_channel(channel_id) #current channel with the given channel id

    if current_channel['standup']['is_active']:
        standup_send_v1(token, channel_id, message)
        return

    if len(message) > 1000:
        raise InputError(f"Message more than 1000 characters")
    if auth_user['u_id'] not in current_channel['all_members']:
        raise AccessError(f"the authorised user has not joined the channel they are trying to post to")
    
    current_time = current_unix_timestamp() #gives us the current timestamp
    current_message = {}
    current_message['message_id'] = next_message_id['id'] #message_id
    current_message['channel_id'] = channel_id
    current_message['dm_id'] = -1 #this is a channel message not dm so for all dm's give -1
    current_message['author_id'] = auth_user['u_id']
    current_message['message'] = message
    current_message['reacts'] = []
    current_message['time_created'] = current_time
    current_message['is_pinned'] = False
    current_channel['messages'].append(current_message['message_id']) 
    next_message_id['id'] += 1 #update the global message id so we get unique ids 

    message_words = message.split(' ')

    # Standup start checker
    # Start a standup if message is exactly "/standup X" where X is a number of seconds
    if message.startswith('/standup') and len(message_words) == 2 and message_words[1].isdigit():
        duration = int(message_words[1])
        standup_start_v1(token, channel_id, duration)

    #notications checker and handler 
    contains_tag = False
    tag_strings = []
    if '@' in message:
        for word in message_words:
            if word.startswith('@'):
                tag_strings.append(word[1:])
                contains_tag = True
    if contains_tag:
        for user_id in current_channel['all_members']:
            user = user_from_id(user_id)
            if user['handle_str'] in tag_strings:
                send_channel_tag_notification(auth_user['handle_str'], user_id, channel_id, message)

    messages.append(current_message)

    update_user_message_stats(auth_user['u_id'])

    update_message_stats()
    
    return {
        'message_id': current_message['message_id'] #message_id
    }

def message_remove_v1(token, message_id):
    """Summary
        Given a message_id for a message, this message is removed from the channel/DM
    Args:
        token (string): A user session token
        message_id (int): A message id number

    Returns:
        Empty dictionary
    
    Raises:
        AccessError: 
            when none of the following are true:
                Message with message_id was sent by the authorised user making this request
                The authorised user is an owner of this channel (if it was sent to a channel) or the **Dreams**
        InputError: Message (based on ID) no longer exists
    """

    check_token(token)
    auth_user = user_from_token(token)

    is_channel_message = False
    for msg in messages:
        if msg['message_id'] == message_id:
            is_channel_message = (msg['channel_id'] != -1) # If channel_id is -1, it is a dm message
            can_remove = False
            if auth_user['u_id'] == msg['author_id'] or is_dreams_owner(auth_user['u_id']):
                # If the user is the author of the message or a dreams owner, they can always edit it
                can_remove = True
            elif msg['channel_id'] != -1 and is_channel_owner(auth_user['u_id'], msg['channel_id']): 
                # If the message was sent to a channel and the user is the channel owner
                can_remove = True
            if can_remove:
                author_id = msg['author_id']
                # delete from messages
                cleared_messages = [msg for msg in messages if msg['message_id'] != message_id]
                messages.clear()
                for msg in cleared_messages:
                    messages.append(msg)

                update_user_message_stats(author_id)

                update_message_stats()

                # delete from channel
                if is_channel_message:
                    for channel in channels:
                        if msg['message_id'] in channel['messages']:
                            channel['messages'] = [m for m in channel['messages'] if m != msg]
                else:
                    # delete from dm
                    for dm in dms:
                        if msg['message_id'] in dm['messages']:
                            dm['messages'] = [m for m in dm['messages'] if m != msg]
                return {}
            else:
                raise AccessError(f"User {auth_user['handle_str']} does not have permission to remove message with id {message_id}")
    raise InputError(f"Message with id {message_id} no longer exists")
        

def message_edit_v2(token, message_id, message):
    """Summary
        Given a message, update its text with new text. If the new message is an empty string, the message 
        is deleted.
    Args:
        token (string): A user session token
        message_id (int): A message id number
        message (string): The text with which the user wishes to replace the current message
    
    Returns:
        Empty dictionary
    
    Raises:
        AccessError: When an invalid token is given, or the user attempts to delete a message that they did
                     not write, or one in a channel that they do not own, and they are not a dreams owner
        InputError: If the message is not a string, is longer than 1000 characters, or message_id does not
                    refer to a valid message
    """
    global messages
    check_token(token)
    auth_user = user_from_token(token)

    if type(message) != str:
        raise InputError(f"Message {message} is not of type string")

    if len(message) > 1000:
        raise InputError(f"Length of message is over 1000 characters (length is {len(message)})")

    for msg in messages:
        if msg['message_id'] == message_id:
            can_edit = False
            if auth_user['u_id'] == msg['author_id'] or is_dreams_owner(auth_user['u_id']):
                # If the user is the author of the message or a dreams owner, they can always edit it
                can_edit = True
            elif msg['channel_id'] != -1 and is_channel_owner(auth_user['u_id'], msg['channel_id']): 
                # If the message was sent to a channel and the user is the channel owner
                can_edit = True

            if can_edit:
                if not len(message): # If the new message text is blank, delete the message
                    message_remove_v1(token, message_id)
                else: # Replace the current message text with the new text
                    msg['message'] = message
                return {}
            raise AccessError(f"User {auth_user['handle_str']} does not have permission to edit message with id {message_id}")

    raise InputError(f"Message with id {message_id} does not exist (it may have been deleted)")

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    Summary:
        og_message_id is the original message. 
        
        channel_id is the channel that the message is being shared to, 
        and is -1 if it is being sent to a DM. 
        
        dm_id is the DM that the message is being shared to, 
        and is -1 if it is being sent to a channel.
        
        message is the optional message in addition to the shared message, 
        and will be an empty string '' if no message is given   
    Args:
        token (string): A user session token 
        og_message_id (int): the message id of the original message
        message (string): a message string added to the shared message
        channel_id (int): A channel_id number -1 if we are sharing to dms
        dm_id (int): A message_id number -1 if send to we are sharing to channels
    Returns: 
        dictionary which contains the shared_message_id
    Raises:
        AccessError when:
            the authorised user has not joined the channel or DM they are trying to share the message to
    '''
    global users, channels, next_message_id, dms, messages
    assert check_token(token)
    auth_user_id = user_from_token(token)['u_id']
    og_message_text = get_message_from_message_id(og_message_id)['message']

    shared_message = message + '\n\n' + og_message_text
    is_channel_message = (channel_id != -1)
    shared_message_id = -1
    if is_channel_message:
        if is_channel_member(auth_user_id, channel_id):
            shared_message_id = message_send_v2(token, channel_id, shared_message)['message_id']
        else:
            raise AccessError(f"Authorised user with id {auth_user_id} has not joined the channel they are trying to share the message to")
    else:
        if is_dm_member(dm_id, auth_user_id):
            shared_message_id = message_senddm_v1(token, dm_id, shared_message)['message_id']
        else:
            raise AccessError(f"Authorised user with id {auth_user_id} has not joined the DM they are trying to share the message to")
    return {
        'shared_message_id' : shared_message_id
    }

def message_senddm_v1(token, dm_id, message):
    """Summary
        Send a message from authorised_user to the DM specified by dm_id. Note: Each message should have it's own unique ID. I.E. 
        No messages should share an ID with another message, even if that other message is in a different channel or DM.
    Args:
        token (string): A user session token
        dm_id (int): A dream id number which the message will be sented to
        message (string): The text with which the user wishes to sent to dream
    
    Returns:
        Dictionary: { message_id } the new message
    
    Raises:
        AccessError: when:  the authorised user is not a member of the DM they are trying to post to
        InputError: Message is more than 1000 characters
    """
    global next_message_id
    check_token(token)
    auth_user = user_from_token(token)

    # InputError: Message is more than 1000 characters
    if len(message) > 1000:
        raise InputError(f"Message {message} is more than 1000 characters")
    
    for dm in dms:
        if dm['dm_id'] == dm_id: 
            # AccessError: when:  the authorised user is not a member of the DM they are trying to post to
            if auth_user['u_id'] not in dm['members']:
                raise AccessError(f"the authorised user is not a member of the DM {dm_id}")
            else:
                current_time = current_unix_timestamp()
                message_id = next_message_id['id']
                next_message_id['id'] += 1

                # create a new message which will be sent to the dm
                current_message = {}
                current_message['message_id'] = message_id
                current_message['channel_id'] = -1
                current_message['dm_id'] = dm_id 
                current_message['author_id'] = auth_user['u_id']
                current_message['message'] = message
                current_message['reacts'] = []
                current_message['time_created'] = current_time
                current_message['is_pinned'] = False

                contains_tag = False
                tag_strings = []

                if '@' in message:
                    for word in message.split(' '):
                        if word.startswith('@'):
                            tag_strings.append(word[1:])
                            contains_tag = True

                # the massage is already in the taget dm, send a notification
                if contains_tag:
                    for user_id in dm['members']:
                        user = user_from_id(user_id)
                        if user['handle_str'] in tag_strings:
                            send_dm_tag_notification(auth_user['handle_str'], user_id, dm_id, message)

                # add the new massage to the messages list in the data
                dm['messages'].append(message_id)
                messages.append(current_message)

                update_user_message_stats(auth_user['u_id'])

                update_message_stats()

                return { 
                    'message_id': message_id 
                }
    raise InputError(f"DM id {dm_id} does not refer to a valid dm")

def message_sendlater_v1(token, channel_id, message, time_sent):
    """Summary
        Send a message from authorised_user to the channel specified by channel_id automatically at a specified time in the future
    Args:
        token (string): A user session token
        channel_id (int): A channel id number which the message will be sented to
        message (string): The text with which the user wishes to sent to channel
        time_sent (int): the time of when this message will be sent
    
    Returns:
        Dictionary: { message_id } the new message
    
    Raises:
        AccessError: the authorised user has not joined the channel they are trying to post to
        InputError:  Channel ID is not a valid channel
                     Message is more than 1000 characters
                     Time sent is a time in the past
    """

    # current_time = current_unix_timestamp()
    # time_intervel = time_sent - current_time

    # # InputError: Time sent is a time in the past
    # if time_intervel < 0:
    #     raise InputError("Time sent is a time in the past")
    
    # time.sleep(time_intervel)
    # message_id = message_send_v2(token, channel_id, message)
    
    # return { 'message_id': message_id }

    global users, channels, next_message_id, messages
    assert check_token(token)

    if valid_channel(channel_id) == False:
        raise InputError(f"Channel ID {channel_id} is not a valid channel") 

    # InputError: Message is more than 1000 characters
    if len(message) > 1000:
        raise InputError(f"Message {message} is more than 1000 characters")

    current_time = current_unix_timestamp()
    time_intervel = time_sent - current_time
    
    # if datetime.fromtimestamp(time_sent) < datetime.fromtimestamp(current_time):
    #     raise InputError("Time sent is a time in the past")

    # InputError: Time sent is a time in the past
    if time_intervel < 0:
        raise InputError("Time sent is a time in the past")
    
    auth_user = user_from_token(token)
    current_channel = find_channel(channel_id) #current channel with the given channel id

    if auth_user['u_id'] not in current_channel['all_members']:
        raise AccessError(f"the authorised user has not joined the channel they are trying to post to")
    
    message_id = next_message_id['id']
    next_message_id['id'] += 1

    future_message = {}
    future_message['message_id'] = message_id #message_id
    future_message['channel_id'] = channel_id
    future_message['dm_id'] = -1 #this is a channel message not dm so for all dm's give -1
    future_message['author_id'] = auth_user['u_id']
    future_message['message'] = message
    future_message['reacts'] = []
    future_message['time_created'] = time_sent
    future_message['is_pinned'] = False

    future_messages.append(future_message)

    return {
        'message_id': future_message['message_id'] #message_id
    }


def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    """Summary
        Send a message from authorised_user to the dm specified by dm_id automatically at a specified time in the future
    Args:
        token (string): A user session token
        dm_id (int): A dm id number which the message will be sented to
        message (string): The text with which the user wishes to sent to dm
        time_sent (int): the time of when this message will be sent
    
    Returns:
        Dictionary: { message_id } the new message
    
    Raises:
        AccessError: the authorised user has not joined the dm they are trying to post to
        InputError:  dm ID is not a valid dm
                     Message is more than 1000 characters
                     Time sent is a time in the past
    """

    # current_time = current_unix_timestamp()
    # time_intervel = time_sent - current_time

    # # InputError: Time sent is a time in the past
    # if time_intervel < 0:
    #     raise InputError("Time sent is a time in the past")
    
    # time.sleep(time_intervel)
    # message_id = message_senddm_v1(token, dm_id, message)
    
    # return { 'message_id': message_id }

    

    global users, dms, next_message_id, messages
    assert check_token(token)

    # InputError:  dm ID is not a valid dm
    if valid_dm(dm_id) == False:
        raise InputError(f"DM ID {dm_id} is not a valid dm") 

    # InputError: Message is more than 1000 characters
    if len(message) > 1000:
        raise InputError(f"Message {message} is more than 1000 characters")

    current_time = current_unix_timestamp()
    time_intervel = time_sent - current_time

    # InputError: Time sent is a time in the past
    if time_intervel < 0:
        raise InputError("Time sent is a time in the past")
    
    auth_user = user_from_token(token)
    current_dm = find_dm(dm_id) #current dm with the given dm id

    if auth_user['u_id'] not in current_dm['members']:
        raise AccessError(f"the authorised user has not joined the dm they are trying to post to")
    
    message_id = next_message_id['id']
    next_message_id['id'] += 1

    future_message = {}
    future_message['message_id'] = message_id #message_id
    future_message['dm_id'] = dm_id
    future_message['channel_id'] = -1 #this is a dm message not dm so for all dm's give -1
    future_message['author_id'] = auth_user['u_id']
    future_message['message'] = message
    future_message['reacts'] = []
    future_message['time_created'] = time_sent
    future_message['is_pinned'] = False

    future_messages.append(future_message)
    
    return {
        'message_id': future_message['message_id'] #message_id
    }

def message_react_v1(token, message_id, react_id):
    """Summary
        Given a message, update its text with new text. If the new message is an empty string, the message 
        is deleted.
    Args:
        token (string): A user session token
        message_id (int): A message id number
        react_id (int): the react type of this react, (only the 1 for now)
    
    Returns:
        Empty dictionary
    
    Raises:
        AccessError: The authorised user is not a member of the channel or DM that the message is within
        InputError: message_id is not a valid message within a channel or DM that the authorised user has joined
                    react_id is not a valid React ID. The only valid react ID the frontend has is 1
                    Message with ID message_id already contains an active React with ID react_id from the authorised user
    """
    global messages

    check_token(token)
    auth_user = user_from_token(token)
    user_id = auth_user['u_id']

    # react_id is not a valid React ID. The only valid react ID the frontend has is 1
    if react_id != 1:
        raise InputError(f"react_id {react_id} is not a valid React ID. The only valid react ID the frontend has is 1")

    message_found = False
    for msg in messages:
        if msg['message_id'] == message_id:
            message_found = True
            if msg['channel_id'] != -1:
                if is_channel_member(user_id, msg['channel_id']) == False:
                    raise AccessError(f"The authorised user {user_id} is not a member of the channel that the message is within")
                send_channel_message_react_notification(user_id, msg['author_id'], msg['channel_id'])
            if msg['dm_id'] != -1:
                if is_dm_member(msg['dm_id'], user_id) == False:
                    raise AccessError(f"The authorised user {user_id} is not a member of the dm that the message is within")
                send_dm_message_react_notification(user_id, msg['author_id'], msg['dm_id'])
            # if 'reacts' in msg.keys():
            react_peoples = msg['reacts']
            check_react = False
            # check if this user has already reacted this message
            for react_people in react_peoples:
                if react_people == user_id:
                    check_react = True
                    raise InputError(f"Message {message_id} already contains an active React with ID react_id from the authorised user")
            if check_react == False:
                msg['reacts'].append(user_id)
            # else:
            #     msg['reacts'] = [user_id]
   
        # InputError: message_id is not a valid message within a channel or DM that the authorised user has joined 
    if not message_found:
        raise InputError(f"message_id {message_id} is not a valid message within a channel or DM that the authorised user has joined") 

    return {}


def message_unreact_v1(token, message_id, react_id):
    """Summary
        Given a message within a channel or DM the authorised user is part of, remove a "react" to that particular message
    Args:
        token (string): A user session token
        message_id (int): A message id number
        react_id (int): the react type of this react, (only the 1 for now)
    
    Returns:
        Empty dictionary
    
    Raises:
        AccessError: The authorised user is not a member of the channel or DM that the message is within
        InputError: message_id is not a valid message within a channel or DM that the authorised user has joined
                    react_id is not a valid React ID. The only valid react ID the frontend has is 1
                    Message with ID message_id does not contain an active React with ID react_id from the authorised user
    """
    global messages

    check_token(token)
    auth_user = user_from_token(token)
    user_id = auth_user['u_id']

    # react_id is not a valid React ID. The only valid react ID the frontend has is 1
    if react_id != 1:
        raise InputError(f"react_id {react_id} is not a valid React ID. The only valid react ID the frontend has is 1")

    message_found = False
    for msg in messages:
        if msg['message_id'] == message_id:
            message_found = True
            if msg['channel_id'] != -1:
                if is_channel_member(user_id, msg['channel_id']) == False:
                    raise AccessError(f"The authorised user {user_id} is not a member of the channel that the message is within")
            else:
                if is_dm_member(msg['dm_id'], user_id) == False:
                    raise AccessError(f"The authorised user {user_id} is not a member of the dm that the message is within")
            
            # if 'reacts' in msg.keys():
            react_peoples = msg['reacts']
            check_react = False
            # check if this user has already reacted this message
            for react_people in react_peoples:
                if react_people == user_id:
                    check_react = True
                    msg['reacts'].remove(user_id)
            if check_react == False:
                raise InputError(f"Message {message_id} does not contain an active React with ID react_id from the authorised user")
            # else:
            #     raise InputError(f"Message {message_id} does not contain an active React with ID react_id from the authorised user")
   
        # InputError: message_id is not a valid message within a channel or DM that the authorised user has joined 
    if not message_found:
        raise InputError(f"message_id {message_id} is not a valid message within a channel or DM that the authorised user has joined") 

    return {}

def message_pin_v1(token, message_id):
    '''Summary
        Given a message within a channel or DM, mark it as "pinned" to be given special display treatment by the frontend
    Args:
        token (string): A user session token
        message_id (int): A message_id of the message
    
    Returns:
        A empty dictionary
    
    Raises:
       Raises:
        InputError when:
            message_id is not a valid message
            Message with ID message_id is already pinned
        AccessError when:
            The authorised user is not a member of the channel
            The authorised user is not a member of the DM that the message is within
            The authorised user is not an owner of the channel or DM
    '''
    check_token(token)
    auth_user = user_from_token(token)
    if valid_message(message_id) == False:
        raise InputError("message_id is not a valid message")
    
    message = get_message_from_message_id(message_id)
    
    if message['is_pinned'] == True:
        raise InputError("Message with ID message_id is already pinned")
    
    if message['channel_id'] == -1: #this means this is a dm message 
        current_dm = find_dm(message['dm_id'])
        if auth_user['u_id'] not in current_dm['members']:
            raise AccessError("The authorised user is not a member of the DM")
        if auth_user['u_id'] != current_dm['creator']: # this error will get raised twice is this ok? / this is kinda redundent because if u have to be the owner to pin whats the point of checking for members?
            raise AccessError("The authorised user is not an owner of the DM")
        message['is_pinned'] = True
       
    if message['dm_id'] == -1: # this means this a channel message 
        current_channel = find_channel(message['channel_id'])
        if auth_user['u_id'] not in current_channel['all_members']:
            raise AccessError("The authorised user is not a member of the channel")
        if auth_user['u_id'] not in current_channel['owner_members']:
            raise AccessError("The authorised user is not an owner of the channel")
        message['is_pinned'] = True
    
    return {}

def message_unpin_v1(token, message_id):
    '''
    Summary:
        Given a message within a channel or DM, remove it's mark as unpinned
    Args:
        token (string): A user session token 
        message_id (int): A message_id number
    Returns: 
        empty dictionary 
    Raises:
        InputError when:
            message_id is not a valid message
            Message with ID message_id is already unpinned
        AccessError when:
            The authorised user is not a member of the channel or DM that the message is within
            The authorised user is not an owner of the channel or DM
    '''
    check_token(token)
    auth_user = user_from_token(token)
    if valid_message(message_id) == False:
        raise InputError("message_id is not a valid message")
    
    message = get_message_from_message_id(message_id)
    
    if message['is_pinned'] == False:
        raise InputError("Message with ID message_id is already unpinned")
    
    if message['channel_id'] == -1: #this means this is a dm message 
        current_dm = find_dm(message['dm_id'])
        if auth_user['u_id'] not in current_dm['members']:
            raise AccessError("The authorised user is not a member of the DM")
        if auth_user['u_id'] != current_dm['creator']:
            raise AccessError("The authorised user is not an owner of the DM")
        message['is_pinned'] = False
       
    if message['dm_id'] == -1: # this means this a channel message 
        current_channel = find_channel(message['channel_id'])
        if auth_user['u_id'] not in current_channel['all_members']:
            raise AccessError("The authorised user is not a member of the channel")
        if auth_user['u_id'] not in current_channel['owner_members']:
            raise AccessError("The authorised user is not an owner of the channel")
        message['is_pinned'] = False
    
    return {}
