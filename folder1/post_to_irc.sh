#!/bin/bash -e
USER = $1
MYPASSWORD = $2
IRC_SERVER = $3
IRC_PORT = $4
CHANNEL = $5
MSG = $6

{
echo NICK $USER
echo USER $USER 8 * : USER
sleep 1
echo PASS $USER:$MYPASSWORD
echo "JOIN CHANNEL"
echo "PRIVMSG $CHANNEL" $MSG
echo QUIT
} | ncat --ssl $IRC_SERVER $IRC_PORT
