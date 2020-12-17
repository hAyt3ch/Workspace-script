def mac_conv(mac, sep=':'):
    segments = mac.split(sep)
    groups = [segments[0:2], segments[2:4], segments[4:]]
    return ''.join(''.join(group) for group in groups)

with open('mac.txt', 'r') as f:
    for mac in f:
        print(mac_conv(mac))