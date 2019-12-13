#!/bin/bash

source playerDefinitions.sh

EXPERIMENT_LOG="experiment.txt"

TEST_SIDELENGTHS="3 4 5 6 7"
TEST_SECONDS="1 3 5 10"

REPEAT_EXPERIMENT=100
SWITCH_AT=50

experiment() {
    A="$1"
    B="$2"

    A_NAME=$3
    B_NAME=$4

    A_WINS=0
    B_WINS=0
    DRAWS=0

    date | tee -a $EXPERIMENT_LOG
    echo "Currently experimenting: $A_NAME vs $B_NAME." | tee -a $EXPERIMENT_LOG

    for i in $(seq 1 $REPEAT_EXPERIMENT)
        do
            python controller.py -s $SECS -q -d -t -l $SIDELENGTH -ca "$A" -cb "$B"
        
            RESULT=$?
        
            if [ $RESULT -eq 1 ]
            then
                if [ $i -le $SWITCH_AT ]
                then
                    A_WINS=$((A_WINS+1))
                else
                    B_WINS=$((B_WINS+1))
                fi
            fi
        
            if [ $RESULT -eq 2 ]
            then
                if [ $i -le $SWITCH_AT ]
                then
                    B_WINS=$((B_WINS+1))
                else
                    A_WINS=$((A_WINS+1))
                fi
            fi
                    
            if [ $RESULT -eq 3 ]
            then
                DRAWS=$((DRAWS+1))
            fi
                    
            if [ $i -eq $SWITCH_AT ]
            then
                echo "Switching sides, it's $i." | tee -a $EXPERIMENT_LOG
                TMP=$B
                B=$A
                A=$TMP
                            
            fi
        
        done
        echo "Experiment over. $A_NAME: $A_WINS, $B_NAME: $B_WINS, Draws: $DRAWS." | tee -a $EXPERIMENT_LOG


}

for SECS in $TEST_SECONDS
do
    echo "Experiments allowing $SECS second(s) to decide a move." | tee -a $EXPERIMENT_LOG
    for SIDELENGTH in $TEST_SIDELENGTHS
    do
        echo "Experiments with a $SIDELENGTH by $SIDELENGTH gameboard." | tee -a $EXPERIMENT_LOG
        
        experiment "$C1" "$C1T1" "C1" "C1T1"
        
        experiment "$C1" "$C1T2" "C1" "C1T2"
        
        experiment "$C1T1" "$C1T2" "C1T1" "C1T2"
        
        experiment "$C1" "$C1Q" "C1" "C1Q"
        
        experiment "$C1" "$C4" "C1" "C4"
        
        experiment "$C1Q" "$C5" "C1Q" "C5"
        
        experiment "$C1Q" "$C6" "C1Q" "C6"
        
        experiment "$C1Q" "$C7" "C1Q" "C7"
        
        experiment "$C5" "$C6" "C5" "C6"
        
        experiment "$C5" "$C7" "C5" "C7"
        
        experiment "$C6" "$C7" "C6" "C7"
        
    done
done