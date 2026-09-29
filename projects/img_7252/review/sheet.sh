#!/bin/zsh
v=$1; p=$2; shift 2; i=0
rm -f review/${p}_*.png(N)
for t in "$@"; do ffmpeg -v error -y -ss $t -i $v -frames:v 1 -vf "scale=360:-1,drawtext=text='$t':x=8:y=8:fontsize=26:fontcolor=yellow:box=1:boxcolor=black" review/${p}_$(printf %02d $i).png; i=$((i+1)); done
ffmpeg -v error -y -framerate 1 -i review/${p}_%02d.png -vf "tile=$(( i<6?i:6 ))x$(( (i+5)/6 )):color=black" -frames:v 1 review/${p}_sheet.png
