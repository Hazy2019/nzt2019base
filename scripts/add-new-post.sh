#!/bin/bash
function usage() 
{
  echo $0 "<title>" "category" "tag1" "tag2" ...
}

function output()
{
  if [[ $# < 3 ]]; then
    usage()
  fi
  tl=$1
  cg=$2
  for i in {3..$#}; do
    echo $i
  done
}
