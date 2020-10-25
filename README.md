# VC-Wait-Bot

## To Do:
* Get front of the queue
* Have bot move front of queue from waitroom to playing
* Handle the case of lobby channel and active channel being the same
* Manage role is broken
* jointime = 0 bug still exists - Might be fixed now

## Done:
* Log when user joins VC
* Log when user leaves VC
* Print ordered list when asked
* Grace period for temporary DCs
* On restart add all users to queue if they weren't there
* Settings:
    * Wait channel
    * Grace period
    * Queue Role
* Twitch integration
* Longer term options
    * Play room
    * Time played
* Delete user's command text if bot has perms and user is unprivileged
* Reset wait times
* Need to handle the case of being added to a server while people are in the VC or when config changes

## Commands layout:
* Lobby
    * lobby
        * waiting
        * queue
    * active
        * playing

* Lobby Admin
    * grace
    * activechannel
        * playactive
    * lobbychannel
        * waitchannel
        * queuechannel
    * resetactive
        * resetplaying
    * resetlobby
        * resetwaiting
        * resetqueue
* Admin
    * config
    * cooldown
    * managerole
    * privilegecommands
* Twitch
    * addtwitch
    * removetwitch
    * showtwitch

