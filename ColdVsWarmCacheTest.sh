#!/bin/bash
set -euxo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: ${0} <<IP address of prime challenge server>>"
    exit 1
fi

PRIME_SERVER="${1}"

jobid=$(curl --request POST "http://${PRIME_SERVER}:8080/Start/1,3")
echo ${jobid}
curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}"

STARTTIME=$(date +%s)
jobid=$(curl --request POST "http://${PRIME_SERVER}:8080/Start/1,1234567")
echo ${jobid}
until ! curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}" -v 2>&1 | grep "HTTP/1.0 204"; do
    printf '.'
    sleep 1
done
curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}"
ENDTIME=$(date +%s)
cold_cache_duration=$(($ENDTIME - $STARTTIME))
echo "It took $cold_cache_duration seconds get the prime numbers from a cold cache state"

STARTTIME=$(date +%s)
jobid=$(curl --request POST "http://${PRIME_SERVER}:8080/Start/1,1234567")
echo ${jobid}
until ! curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}" -v 2>&1 | grep "HTTP/1.0 204"; do
    printf '.'
    sleep 1
done
curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}"
ENDTIME=$(date +%s)
warm_cache_duration=$(($ENDTIME - $STARTTIME))
echo "It took $warm_cache_duration seconds get the prime numbers from a warm cache state"
echo "$warm_cache_duration should be much less than $cold_cache_duration"
