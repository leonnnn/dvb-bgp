#!/usr/bin/python3

import ipaddress

lines = {
    "linie_01.txt",
    "linie_02.txt",
    "linie_03.txt",
    "linie_04.txt",
    "linie_06.txt",
    "linie_07.txt",
    "linie_08.txt",
    "linie_09.txt",
    "linie_10.txt",
    "linie_11.txt",
    "linie_12.txt",
    "linie_13.txt",
}

def station_to_str(station):
    ret = station.strip()
    ret = ret.replace("ß", "ss")
    ret = ret.replace("ä", "ae")
    ret = ret.replace("ü", "ue")
    ret = ret.replace("ö", "oe")
    ret = ret.replace(" ", "")
    ret = ret.replace("/", "")
    ret = ret.replace("-", "")
    ret = ret.replace(".", "")
    ret = ret.replace(",", "")
    ret = ret.replace("(", "")
    ret = ret.replace(")", "")
    ret = ''.join([i if ord(i) < 128 else '' for i in ret])
    return ret

stations = set()
for line in lines:
    with open(line, "r") as f:
        for station in f.readlines():
            stations.add(station.strip())

print("graph dvb {")
print('    node [ipv6_forwarding="on",')
print('          exec="bird6 -d -c {{ file_from_template(\'bird6.conf.jinja\') }} -s birdsock-{{ node.get_name() }}"];')

asn = 64513
loopback_pool = ipaddress.IPv6Network("2001:db8::/112").hosts()
for station in stations:
    print('    {node} [AS={asn},loopback="{loopback}"];'.format(
        node=station_to_str(station),
        asn=asn,
        loopback=next(loopback_pool)
    ))
    asn += 1

print()

def get_interface():
    i = 0
    while True:
        yield "veth{}".format(i)
        i += 1



# add edges
unique_edges = set()

for line in lines:
    with open(line, "r") as f:
        linestations = [station_to_str(s) for s in f.readlines()]

    last = linestations[0]
    for linestation in linestations[1:]:
        if last < linestation:
            unique_edges.add((last, linestation))
        else:
            unique_edges.add((linestation, last))

        last = linestation

transfernet_pool = ipaddress.IPv6Network("2001:db8:0:0:1::0/80")
transfernet_pool_it = transfernet_pool.subnets(new_prefix=127)
interface_it = get_interface()

for src, dst in unique_edges:
    transfernet = next(transfernet_pool_it)
    leftip, rightip = list(transfernet)
    print('    {src} -- {dst} [leftif="{leftif}",rightif="{rightif}",leftip="{leftip}/127",rightip="{rightip}/127"];'.format(
        src=src,
        dst=dst,
        leftif=next(interface_it),
        rightif=next(interface_it),
        leftip=leftip,
        rightip=rightip,
    ))

print("}")
