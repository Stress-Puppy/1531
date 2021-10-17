# Assumptions

* channel_id and user_id values cannot be negative (>=0) 

* auth_register_v1 does nothing to the key permission and channel 

* channel_join_v1 does nothing when given the user_id of a user that is already a member of the channel 

* Global permissions are stored as a single entry in each user's dictionary, an integer which is either 1 or 2 and has the key 'permission' 

* A user with the global permission 'owner' (permission id 1) can join private channels and automatically be placed in the 'owner_members' list regardless of whether or not they were invited 

* A user's permissions in a channel are determined by their inclusion in the 'owner_members' list or the 'all_members' list. I.e. if they are in 'owner_members', they are a channel owner 

* All users are assigned the global 'member' permission (permission id 2) by default when registered 

* The owners in 'owner_members' will also be members inside the channel in 'all_members'  

* All members in a channel can view the list of owners and members inside that channel  

* The 'auth_user_id' input parameter to the function "channels_listall_v1" has no effect on the function's operation, as none is specified in the project specifications 

* No email can be used to register more than one user 

* "start" input parameter of channel_messages_v1 cannot be negative and the function will raise an InputError if given a negative "start" value 

* Cannot invite a user to a channel if they are already a member of that channel (discuss)/cameron 

* For channel_list if the Auth user is not a part of any channel instead of returning an empty list we return that the user is not in any channel 