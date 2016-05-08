#!/bin/bash

for s in $(seq 0 7); 
do
    for c in $(seq -3 3); 
    do
        for e in $(seq -10 -3); 
        do 
            ../libraries/liblinear-2.1/train -s $s -c $c -e 1e$e -v 10 -q raw_features_scale > ../results/unscaled/_s${s}_c${c}_e${e}.result &
        done
    done
done
