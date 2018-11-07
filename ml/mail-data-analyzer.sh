#!/bin/bash

# Script to run python program
# The script is called from scheduled job every minute that runs on ec2 server

echo "Script Started: ${0}"

WORKING_DIR="$(dirname "$0")"

# clean temp folder
[ -f ${WORKING_DIR}/temp/email.txt ] && rm ${WORKING_DIR}/temp/email.txt
[ -f ${WORKING_DIR}/temp/output.txt ] && rm ${WORKING_DIR}/temp/output.txt
[ -f ${WORKING_DIR}/temp/mail-data-for-visualization.json ] && rm ${WORKING_DIR}/temp/mail-data-for-visualization.json

# call python script
python /home/ec2-user/scripts/analyzer.py

#
echo "Script Completed: ${0}"