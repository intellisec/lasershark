#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"


bash $SCRIPT_DIR/preprocess.sh
bash $SCRIPT_DIR/evalPreprocessing.sh
bash $SCRIPT_DIR/parse.sh
bash $SCRIPT_DIR/evaluating.sh