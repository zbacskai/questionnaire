#!/bin/bash

find . -name '*json' | while read JSON_FILE
do
    echo $JSON_FILE
    curl -vX POST http://localhost:5000/0.1/questionnaires/create -d @${JSON_FILE} --header "Content-Type: application/json"
done


