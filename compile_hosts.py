#!/usr/bin/env python3

# This script compiles the hosts file into a grossly-simplified version
# named nimbus-hosts, which is processed by Nimbus to block ads.

f = open("hosts", "r")
host_rules = [line.split(" ")[1].replace("\n", "") for line in f.readlines() if len(line.split(" ")) > 1 and not line.startswith("#") and len(line) > 1]
host_rules = [line for line in host_rules if line != ""]
f.close()
f = open("nimbus-hosts", "w")
f.write("\n".join(host_rules))
f.close()
