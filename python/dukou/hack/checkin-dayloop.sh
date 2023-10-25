#!/bin/bash
checkInLoop(){
while true
do
    /usr/local/bin/python /app/python/dukou/checkin.py >> /var/log/checkin.log 2>&1
    sleep 86400
done
}
watchCheckInLog(){
  tail -f /var/log/checkin.log
}

watchCheckInLog &
checkInLoop
