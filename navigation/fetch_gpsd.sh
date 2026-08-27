#!/usr/bin/env bash
set -euo pipefail
echo "This helper intentionally does not silently download licensed NMEA standards."
echo "Clone the open-source GPSD project and use one of its regression/test NMEA logs with gpsfake."
echo "GPSD project: https://gitlab.com/gpsd/gpsd"
echo
echo "Example workflow:"
echo "  git clone https://gitlab.com/gpsd/gpsd.git external/gpsd"
echo "  cd external/gpsd"
echo "  ./gpsfake --slow test/daemon/<selected-log>"
