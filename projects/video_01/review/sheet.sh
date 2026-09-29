#!/bin/zsh
# uso: sheet.sh <video> <prefixo> t1 t2 ...
v=$1; p=$2; shift 2; i=0
for t in "$@"; do ffmpeg -v error -y -ss $t -i $v -frames:v 1 -vf "scale=960:-1,drawtext=text='$t':x=10:y=10:fontsize=28:fontcolor=yellow:box=1:boxcolor=black" review/${p}_$(printf %02d $i).png; i=$((i+1)); done
ffmpeg -v error -y -framerate 1 -i review/${p}_%02d.png -vf "tile=3x$(( (i+2)/3 )):color=black" -frames:v 1 review/${p}_sheet.png
