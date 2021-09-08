#!/bin/bash
my_dir=$(cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
source "$my_dir/env.sh"

bash $my_dir/createDirs.sh

python "$my_dir/parseDeviceTrees.py"
