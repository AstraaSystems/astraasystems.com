#!/bin/bash
cd /mnt/d/ARKA_HQ/repos/ardhanarishvara_git
/usr/bin/python3 astraa_billing_run.py >> astraa_data/billing_cron.log 2>&1
