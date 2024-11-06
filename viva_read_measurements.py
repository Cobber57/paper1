# Gets the required measuremnt from RIPE ATLAS and creates the initial dictionary file 
# info from https://ripe-atlas-cousteau.readthedocs.io/_/downloads/en/latest/pdf/
# the official python wrapper around RIPE Atlas API
# 1. measurement type
# The first step is to create the measurement specification object. Currently you can use the following measurement
# types objects:
#• Ping
#• Traceroute
#• Dns
#• Sslcert
#• Ntp
#• Http

from ripe.atlas.cousteau import (
Ping,
Traceroute
)
traceroute = Traceroute(
af=4,
target="www.ripe.net",
description="Traceroute Test",
protocol="ICMP",
)

# 2. Measurement Source


source = AtlasSource(
type="area",
value="WW",
requested=5,
tags={"include":["system-ipv4-works"]}
)
source1 = AtlasSource(
type="country",
value="GB",
requested=50,
tags={"include": ["system-anchor"]}
)
