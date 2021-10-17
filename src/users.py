from src.data import users, channels, dms, dreams_stats
from src.error import InputError, AccessError
from src.helpers import check_token

def users_all_v1(token):
    """Summary
        Returns a list of user details for all existent users.
    Args:
        token (string): User session token
    
    Returns:
        u_dict (dictionary): Single key 'users' that points to a list of user detail dictionaries for all users

    Raises:
        AccessError: When an invalid token value is given
    """
    check_token(token)

    output = { 'users' : [] }
    for user in users:
        if user['permission'] != 0:
            u_dict = { 'u_id' : user['u_id'],
                       'email' : user['email'],
                       'name_first' : user['name_first'],
                       'name_last' : user['name_last'],
                       'handle_str' : user['handle_str'],
                       'profile_img_url' : user['profile_img_url']
                     }
            output['users'].append(u_dict)
    return output

def users_stats_v1(token):
    """Summary
        Fetches the current set of stored usage statistics for the Dreams platform
    Args:
        token (string): A user session token
    
    Returns:
        stats_dict: Dictionary of the form:
                        {
                            channels_exist: [{num_channels_exist, time_stamp}], 
                            dms_exist: [{num_dms_exist, time_stamp}], 
                            messages_exist: [{num_messages_exist, time_stamp}], 
                            utilization_rate 
                        }
    Raises:
        AccessError: When the token parameter is an invalid token

    """
    check_token(token)
    """
    Dictionary of shape {
     channels_exist: [{num_channels_exist, time_stamp}], 
     dms_exist: [{num_dms_exist, time_stamp}], 
     messages_exist: [{num_messages_exist, time_stamp}], 
     utilization_rate 
    }
    """
    # dreams_stats list already contains data in necessary format, excluding utilization

    # Count number of non-removed users in the users list
    num_users = len([user for user in users if user['permission'] != 0])

    util = 0
    active_users = 0

    for user in users: # Determine number of users in at least one channel or dm
        if len(user['channels']) or len(user['dms']):
            active_users += 1
    util = active_users / num_users # Calculate utilization

    stats_dict = dreams_stats.copy()
    stats_dict['utilization_rate'] = util
    return { 'dreams_stats' : stats_dict }