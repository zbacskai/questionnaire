#!/bin/bash
curl -d "{\"name\":\"$1\", \"data\":\"test-data1\"}" -H "Content-Type: application/json" -X POST http://localhost:5000/0.1/questions/create
