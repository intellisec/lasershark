#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

WORKING_DIR=$SCRIPT_DIR/..
cd $WORKING_DIR

bash $SCRIPT_DIR/createDirs.sh

# The absolute path to the linux kernel repository
LINUX_DIR="$WORKING_DIR/linux/"

# Clone linux kernel if not already done
if [ ! -d "$LINUX_DIR" ]; then
  echo "Cloning linux kernel. This takes a while."
  git clone git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git || exit
fi



# Where should the csv file go to
RESULT_DIR="$WORKING_DIR/results/"

# Name of the result file
RESULT_FILE="preprocessingResult.csv"

# Names of the list files
LIST_FILE="listDTS.txt"
LIST_PROCESSED_FILE="listProcessedDTS.txt"


# Remove already existing files
if [ -f "$RESULT_DIR$RESULT_FILE" ]; then
  echo "Removing $RESULT_DIR$RESULT_FILE"
  rm "$RESULT_DIR$RESULT_FILE"
fi

if [ -f "$RESULT_DIR$LIST_PROCESSED_FILE" ]; then
  echo "Removing $RESULT_DIR$LIST_PROCESSED_FILE"
  rm "$RESULT_DIR$LIST_PROCESSED_FILE"
fi

if [ -f "$LINUX_DIR$LIST_FILE" ]; then
  echo "Removing $LINUX_DIR$LIST_FILE"
  rm "$LINUX_DIR$LIST_FILE"
fi

if [ -f "$LINUX_DIR$LIST_PROCESSED_FILE" ]; then
  echo "Removing $LINUX_DIR$LIST_PROCESSED_FILE"
  rm "$LINUX_DIR$LIST_PROCESSED_FILE"
fi

# Change to linux kernel directory
cd $LINUX_DIR || exit

# Remove preprocessed files!
find -iname '*_processed.dts' | xargs -d"\n" rm

# Create a sorted list of all dts files
find -iname '*.dts' | sort >> "$LIST_FILE"

# Preprocess every dts file one by one
echo "Starting the preprocessing. Takes a while."
num=0
cat "$LIST_FILE" | while read line; do

  echo "Processing file '$line'..."
  dir="$(dirname $line)"
  file="$(basename $line)"

  # Try to change to the directory of the dts file
  cd $dir || continue

  # Call the c preprocessor to preprocess the dts file. Executes headers, includes and other macros
  cpp -x assembler-with-cpp -P "$file" -E -Wp,-MD,test.pre.tmp -nostdinc -undef -D__DTS__  -o "$file"'_processed.dts' -I$LINUX_DIR/include/ -I$LINUX_DIR/arch

  # Check if the preprocessing was successfully
  returncode=$?
  if [ "$returncode" -ne "0" ]
  then
    num=$(($num + 1))
    echo "Error! #$num"
  fi
  
  echo "$line , $returncode" >> "$RESULT_DIR$RESULT_FILE"
  #echo $returncode

  # Return to working directory
  cd $LINUX_DIR || exit

done

# Output the number of failed files
echo $num

# Remove old list
rm "$LIST_FILE"

# Generate list of processed files
find -iname '*_processed.dts' | sort >> "$LIST_PROCESSED_FILE"

# Move list to other folder
mv "$LIST_PROCESSED_FILE" "$RESULT_DIR$LIST_PROCESSED_FILE"
