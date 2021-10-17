# Assumptions

* Assume dm_create_v1 produces dm_id values that are positive integers starting from 0 (i.e. the first dm to be created will have dm_id 0, the next will have dm_id 1 etc. 

* Assume that the first user ever to be registered ever is automatically an owner of  **Dreams** as stated in the specifications 

* Assume user_profile_setname_v2 returns an InputError when the name parameters given are not strings. 

* Assume "start" index given to channel_messages_v2 and  dm_messages_v1 cannot be negative 

* Assume that since message_edit_v2 can edit either messages or dms, no two dm messages or channel messages can have the same id number (dm and channel messages are stored in the same list, all messages have a unique id number) 

* Assume that message_edit_v2 raises an InputError when given any non-existent message_id (not just when the message with id message_id has been deleted) 

* Assume that message_edit_v2 raises an InputError when the given message is not a string 

* Assume that a dm's creator is a part of dm['members] list: name should be automatically generated based on the user(s) that is in this dm. The name should be an alphabetically-sorted, comma-separated list of user handles, e.g. 'handle1,handle2,handle3'. 

* Assume that the id of the first user is always 0 (for channel_addowner_v1() function) 

* Assumption when we remove a user with admin/user/remove we remove them from the channels and the dms they are a part of 

* Assume that search is NON CASE SENSITVE  

* Assume that the return value for the dm_messages and channel_messages functions when given a start index of 0 in dms/channels that have no messages is a dictionary of the format specified in the spec, but with messages as an empty list [], start as an int value 0, and end as an int value –1 e.g {'messages' : [], 'start' : 0, 'end' : -1} (Would not make sense to raise an error, since this is quite common behaviour) 

* Assume that a removed user's first name and last name are both replaced with "Removed User" in their user dictionary and in all of their messages upon removal 

* Assume that a removed user's email can be used to register a new user (email is no longer taken) 

* Assume that a removed user does not appear in the dictionary returned by users_all_v1 (To prevent removed users from appearing in drop-down-boxes on frontend)