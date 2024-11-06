
# info from https://ripe-atlas-cousteau.readthedocs.io/_/downloads/en/latest/pdf/
# Attributes and Methods at https://ripe-atlas-sagan.readthedocs.io/en/latest/types.html

from ripe.atlas.cousteau import (
Traceroute
)

# The first step is to create the measurement specification object
traceroute = Traceroute(
af=4,
target="www.ripe.net",
description="Traceroute Test",
protocol="ICMP",
)

#The second step is to create the measurements source(s). In order to do that you have to
# create an AtlasSource object using the arguments type, value, requested, and optionally tags.
# Type as described in the documentation pages should
# be one of the “area”, “country”, “prefix”, “asn”, “probes”, “msm”.

from ripe.atlas.cousteau import AtlasSource
source1 = AtlasSource(
type="country",
value="GB",
requested=50,
tags={"exclude": ["system-anchor"]}
)
