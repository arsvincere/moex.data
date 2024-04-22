#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

import os
from datetime import timedelta, timezone

# Directories
ROOT_DIR =          ""
DOWNLOAD_DIR =      os.path.join(ROOT_DIR, "download")
LIST_DIR =          os.path.join(ROOT_DIR, "list")
RES_DIR =           os.path.join(ROOT_DIR, "res")
LOG_DIR =           os.path.join(ROOT_DIR, "log")
LOG_FILE =          os.path.join(LOG_DIR,  "debug.log")

# Date & time
UTC =               timezone.utc
MSK_TIME_DIF =      timedelta(hours=3)
ONE_DAY =           timedelta(days=1)

