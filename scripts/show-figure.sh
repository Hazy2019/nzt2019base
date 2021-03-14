#!/bin/bash

function showfigure()
{
  name=$1
  echo "{{< figure src=\"../../resources/$name\" title=\"${name}\" >}}"
}
showfigure "$@"
