#!/bin/bash

export EPICS_CA_SERVER_PORT=20000
export EPICS_CA_REPEATER_PORT=20001

python ./zps-ioc.py
#ipython -i ./zps-ioc.py
