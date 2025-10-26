#!/bin/bash

# Documentation if script misused
usage () (
program_name="$0"
if [ ! $# -eq 0 ]; then
  program_name="./"$1
fi
cat << EOF
Usage: 
  $program_name once|periodically
  Options:
    once: Run the program once
    periodically: Run the program periodically in the background
EOF
)

# Check input parameters
if [[ "${BASH_SOURCE[0]}" != "${0}" ]];then
  echo "Script must be executed, not sourced."
  usage ${BASH_SOURCE[0]}
  return
elif [ $# -eq 0 ];then
  echo "Script is missing parameters."
  usage
  exit 1
elif [[ $1 != "once" ]] && [[ $1 != "periodically" ]];then
  echo "Script has wrong parameter '$1'."
  usage
  exit 2
fi

# Start program
echo "Checking dependencies..."
if [[ ! -d "venv" ]]; then
  python -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

echo "Launching program $1..."
python music_lister.py $1
deactivate
