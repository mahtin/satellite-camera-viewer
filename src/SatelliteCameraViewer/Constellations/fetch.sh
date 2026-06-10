:

URL='https://watcheroftheskies.net/constellations/lines_in_20.txt'

AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
REFER="https://google.com" 

curl -L -A "${AGENT}" -e "${REFER}" "${URL}" -O lines_in_20.txt

mv lines_in_20.txt ~/.cache/constellation-boundaries/

