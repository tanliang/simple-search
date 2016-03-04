#!/bin/bash

_input()
{
    name==$(basename "$2")
    type="${name##*.}"
    echo "$1" |while IFS=$'\t' read -r id info score data
    do
        if [ $id > 0 ]; then
            res=`curl -Ss -d "$data" http://$host/set/$type/$info?score=$score`
            if [[ $(echo $res | grep '"success": 1') != "" ]]
            then
                echo $id > $2
            fi
            echo $data
        fi
        #echo "$2"
    done
}

handleInput()
{
    type=${1##*/}
    
    OLDIFS=$IFS
    IFS=$'\n'
    arr=(`cat $1`)
    IFS=$OLDIFS
    
    if [ ${arr[0]} != 0 ] && [ ${arr[1]} != 0 ]; then
        for (( i = 0; i < ${arr[0]} ; i ++ ))
        do
            for (( j = 0; j < ${arr[1]} ; j ++ ))
            do
                _handle "${arr[2]//<tb>/$j}" "${arr[3]/<db>/$i}" "/tmp/search_update_input_$i$j.$type"
            done
        done
    else
        _handle "${arr[2]}" "${arr[3]}" "/tmp/search_update_input_00.$type"
    fi
}

_handle()
{
    id=0
    if [ -f "$3" ]; then
      id=`cat $3`
    fi
    
    sql=${1/<re>/$id}
    c=`echo "$sql" |$2`
    
    _input "$c" "$3"
}

echo "====================== input begin at `date +"%Y-%m-%d %H:%M:%S"` ==========="
host=`cat host.conf`
for f in input/*
do
    handleInput "$f"
done
echo "====================== input done at `date +"%Y-%m-%d %H:%M:%S"` ==========="
