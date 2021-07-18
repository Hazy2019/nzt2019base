#!/bin/bash
function usage() 
{
  echo $0 "<title>" "category" "weight" "tag1" "tag2" ...
}

function generate_post_header()
{
  title=$1
  category=$2
  weight=$3
  args=("$@")
  datestr=$(date '+%Y-%m-%d')
  
  echo "---"
  echo "title: \"$title\""
  echo "date: $datestr"
  echo "categories:"
  echo " - \"$category\""
  echo "weight: $weight"
  echo "tags:"
  for ((i=3;i<$#;i++)); do
    echo " - \"${args[${i}]}\""
  done
  echo "pager: true"
  echo "sidebar: \"right\""
  echo "---"
}

function output() 
{
  if [[ $# -lt 3 ]]; then
    usage
    exit -1
  fi
  titlesub=${1// /-}
  filename="content/drafts/$2_${titlesub}.md"
  echo "generate post file: $filename"
  generate_post_header "$@" | tee $filename
}

output "$@"
