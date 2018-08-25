#!/bin/bash
set -euxo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: ${0} <<IP address of prime challenge server>>"
    exit 1
fi

PRIME_SERVER="${1}"

STARTTIME=$(date +%s)

# Serial request #1
jobid=$(curl --request POST "http://${PRIME_SERVER}:8080/Start/1,1234571")
echo ${jobid}
until ! curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}" -v 2>&1 | grep "HTTP/1.0 204"; do
    printf '.'
    sleep 1
done
curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}"

# Serial request #2
jobid=$(curl --request POST "http://${PRIME_SERVER}:8080/Start/1,1234572")
echo ${jobid}
until ! curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}" -v 2>&1 | grep "HTTP/1.0 204"; do
    printf '.'
    sleep 1
done
curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}"

# Serial request #3
jobid=$(curl --request POST "http://${PRIME_SERVER}:8080/Start/1,1234573")
echo ${jobid}
until ! curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}" -v 2>&1 | grep "HTTP/1.0 204"; do
    printf '.'
    sleep 1
done
curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid}"

ENDTIME=$(date +%s)
serial_duration=$(($ENDTIME - $STARTTIME))
echo "It took ${serial_duration} seconds get 3 sets of prime numbers serially"


STARTTIME=$(date +%s)

# Parallel requests
jobid1=$(curl --request POST "http://${PRIME_SERVER}:8080/Start/1,1234581")
jobid2=$(curl --request POST "http://${PRIME_SERVER}:8080/Start/1,1234582")
jobid3=$(curl --request POST "http://${PRIME_SERVER}:8080/Start/1,1234583")
echo ${jobid1}
echo ${jobid3}
echo ${jobid2}

# Wait for parallel request #1
until ! curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid1}" -v 2>&1 | grep "HTTP/1.0 204"; do
    printf '.'
    sleep 1
done
curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid1}"

# Wait for parallel request #2
until ! curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid2}" -v 2>&1 | grep "HTTP/1.0 204"; do
    printf '.'
    sleep 1
done
curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid2}"

# Wait for parallel request #3
until ! curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid3}" -v 2>&1 | grep "HTTP/1.0 204"; do
    printf '.'
    sleep 1
done
curl --request GET "http://${PRIME_SERVER}:8080/Query/${jobid3}"

ENDTIME=$(date +%s)
parallel_duration=$(($ENDTIME - $STARTTIME))
echo "It took ${parallel_duration} seconds get 3 sets of prime numbers in parallel"

echo "${parallel_duration} should be around 50% or less of ${serial_duration} *if* you have 4 or more cores/CPUs on the PrimeChallenge server"
