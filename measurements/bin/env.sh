#!/bin/bash
my_dir=$(cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

ln_env="$my_dir/../env"
env="$( readlink -f ~/ )/.local/env/lasershark"

function pip_install_colorpy()
{
	pip install -U git+https://github.com/markkness/ColorPy.git#subdirectory=colorpy
	find -H "$ln_env" -path "*/colorpy/ciexyz.py" | xargs sed -i -e 's/^import colormodels/from colorpy import colormodels/'
}

if [ -e "$env" ] && [ -e "$env/bin/activate" ]
then
	source "$env/bin/activate"
else
	python3 -m venv "$env"
	if [ $? -ne 0 ]
	then
		echo "[*] Install python/ virtual environments"
		echo "    apt install python3 python3-pip python3-venv"
		[[ "${BASH_SOURCE[0]}" != "${0}" ]] && return || exit
	fi

	source "$env/bin/activate"
	pip install --upgrade pip
	pip install -r "$my_dir/../requirements.txt"

	pip_install_colorpy

	grep -P '\#' "$my_dir/../requirements.txt"
fi

rm -R "$ln_env" > /dev/null 2>&1
ln -s "$env" "$ln_env"
