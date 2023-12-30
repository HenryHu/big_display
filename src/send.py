#!/usr/bin/env python3

import subprocess
import sys

import local_config

subprocess.check_call(["curl", "http://%s/bitmap/0/0/%d/%d" % (
    local_config.LOCAL_IP, local_config.WIDTH, local_config.HEIGHT), "--data-binary",
    "@%s" % sys.argv[1]])
