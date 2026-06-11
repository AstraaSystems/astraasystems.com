# Runbook

## Start System
python3 execution/autonomous_system.py

## Stop System
touch kill.switch

## Restart
rm kill.switch
python3 execution/autonomous_system.py

## Check Logs
ipc_logs/YYYY-MM-DD.jsonl
logs/system/YYYY-MM-DD.log
