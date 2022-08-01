#!/bin/bash

GAMEDATADIR=$(pwd)/qrogue/data
USERDATADIR=$HOME/.local/share/qrogue
[ -d ${USERDATADIR} ] || mkdir -p ${USERDATADIR}
if [ ! -d ${GAMEDATADIR} ]
then
	echo Game data dir missing!
	exit 1
fi

python3 main.py --from-console -gd $GAMEDATADIR -ud $USERDATADIR $*

