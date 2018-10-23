#!/bin/bash

rm -rvf wth4-maprepo
git clone git@github.com:DiyAI-robocar/wth4-maprepo.git

cd wth4-maprepo
while true; do
  sleep 10
  git pull
done
