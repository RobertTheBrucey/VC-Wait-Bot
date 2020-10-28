#!/bin/bash
#trap "killall python3" RETURN EXIT SIGINT

#python3 twitch.py &
#python3 bot.py &
#while true;do sleep 5;done
if [ -z "$PROFILE" ]; then
    python3 bot.py
else
    python3 -m cProfile -o db/profile bot.py
fi