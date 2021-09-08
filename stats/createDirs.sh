#!/bin/bash


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

WORKING_DIR=$SCRIPT_DIR/..
cd $WORKING_DIR

if [ ! -d "$WORKING_DIR/results" ]; then
	mkdir $WORKING_DIR/results
fi
	
