#!/bin/bash

file=$1

dos2unix $file

while read -r line; do
  name=$(echo $line | cut -d ',' -f1-2)
  address=$(echo $line | cut -d ',' -f4-7 | sed 's/,/ /g' | sed 's/"//g')

  echo $name
  echo $address
  echo

done < $file