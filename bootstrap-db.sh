#/bin/bash

ROOT=$(pwd)
cd ./configuration/abtest && ./store-abtest.sh && cd $ROOT
cd ./configuration/questionnaires && ./store-questionnaires.sh && cd $ROOT
cd ./configuration/questions && ./store-questions.sh && cd $ROOT

