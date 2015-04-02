#!/bin/bash
prefix="lvs.dg.172_28_26_82."
statsd="10.10.18.20"
port="9101"

function push_statsd() {
    key=$1
    value=$2
    type=$3
    echo "$key:$value|$type"
    echo "$key:$value|$type" | nc -u -w0 $statsd $port
}

function gauge() {
    before=$1
    after=$2
    return `echo $before $after`

}

function
while :
do
    ipvsadm -Ln --stats --exact |grep -E  "TCP|UDP" | while read line;
    do
       protocol=`echo $line|awk '{print $1}'`
       vip=`echo $line|awk '{print $2}'|sed 's/\./_/g' |sed 's/:/_/'`
       before_conn=`echo $line|awk '{print $3}'`
       before_inpkts=`echo $line|awk '{print $4}'`
       before_outpkts=`echo $line|awk '{print $5}'`
       before_inbytes=`echo $line|awk '{print $6}'`
       before_outbytes=`echo $line|awk '{print $7}'`
       push_statsd "$prefix.$protocol.$vip.conns" `echo $before_conn` "c"
    done

    sleep 10

    ipvsadm -Ln --stats --exact |grep -E  "TCP|UDP" | while read line;
    do
       protocol=`echo $line|awk '{print $1}'`
       vip=`echo $line|awk '{print $2}'|sed 's/\./_/g' |sed 's/:/_/'`

    done


   push_statsd "$prefix.$protocol.$vip.conns" "$conn" "c"
   push_statsd "$prefix.$protocol.$vip.inpkts" "$inpkts" "c"
   push_statsd "$prefix.$protocol.$vip.outpkts" "$outpkts" "c"
   push_statsd "$prefix.$protocol.$vip.inbytes" "$inbytes" "c"
   push_statsd "$prefix.$protocol.$vip.outbytes" "$outbytes" "c"

echo "action..."
done