#!/bin/bash

PATH_TO_KEY=
PATH_TO_DATA=

docker run -d --restart=unless-stopped --name="birthday-remainder" \
    -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro \
    -v ${PATH_TO_DATA}:/app/data.xlsx:ro \
    -v ${PATH_TO_KEY}:/app/key:ro \
    birthday-remainder:latest