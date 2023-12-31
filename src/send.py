#!/usr/bin/env python3

import subprocess
import sys

import local_config

if len(sys.argv) < 2:
    filename = 'out.bmp'
else:
    filename = sys.argv[1]

subprocess.check_call(["curl", "http://%s/bitmap?w=%d&h=%d" % (
    local_config.LOCAL_IP, local_config.WIDTH, local_config.HEIGHT), "--data-binary",
    "@%s" % filename, "-H", "Content-Type: application/binary"])
