<!-- topics: networking -->
# Networking Fundamentals: Practical Notes

## IPv4 addressing and subnet math
An IPv4 address has 32 bits, written as four decimal octets such as 192.168.10.77. The prefix length (CIDR notation, for example /26) says how many leading bits identify the network. The remaining bits identify the host inside that network.
The number of addresses in a subnet is 2 to the power of (32 minus prefix). Usable host addresses are that number minus 2, because the first address is the network address and the last is the broadcast address. A /24 has 256 addresses and 254 usable hosts. A /26 has 64 addresses and 62 usable hosts. A /30 has 4 addresses and 2 usable hosts, which is why /30 was traditionally used for point-to-point links. A /31 is a special case allowed on point-to-point links (RFC 3021) with no network or broadcast address.
The subnet mask is the same information in dotted form. /24 is 255.255.255.0, /25 is 255.255.255.128, /26 is 255.255.255.192, /27 is 255.255.255.224, /28 is 255.255.255.240, /29 is 255.255.255.248, /30 is 255.255.255.252.

## How to find the network and broadcast address quickly
Find the interesting octet, the one where the mask is not 255 or 0. Compute the block size as 256 minus the mask value in that octet. Network addresses are multiples of the block size.
Example: 192.168.10.77/26. The mask in the last octet is 192, so the block size is 256 minus 192 which is 64. The blocks start at 0, 64, 128, 192. The address .77 falls in the block starting at 64. So the network address is 192.168.10.64, the broadcast address is 192.168.10.127, and the usable hosts are .65 to .126.
Example: how many /27 subnets fit in a /24? A /27 adds 3 bits to the /24, so there are 2 to the power of 3, which is 8 subnets, each with 32 addresses (30 usable).

## Special and private IPv4 ranges
Private addresses that are not routed on the public internet: 10.0.0.0/8, 172.16.0.0/12 (that is 172.16.0.0 to 172.31.255.255), and 192.168.0.0/16.
Loopback is 127.0.0.0/8, and 127.0.0.1 is localhost. Link-local addresses 169.254.0.0/16 appear when a device fails to get an address from DHCP (called APIPA on Windows). The range 100.64.0.0/10 is used by carriers for carrier-grade NAT.
A common beginner mistake is to think 172.32.x.x is private. It is not. Only 172.16 through 172.31 is private.

## NAT
Network Address Translation lets many private hosts share one public IPv4 address. Home routers do PAT (port address translation, also called NAT overload): the router rewrites the source address and source port of outgoing packets and remembers the mapping in a translation table so replies can be sent back to the right internal host.
NAT is one reason inbound connections to a home network fail by default. To expose a service you need port forwarding, a VPN, or a tunnel. NAT is not a security feature by itself, although the default behaviour of dropping unsolicited inbound traffic helps in practice.

## IPv6 basics
IPv6 addresses are 128 bits, written as eight groups of four hex digits, for example 2001:0db8:0000:0000:0000:0000:0000:0001. Leading zeros in a group can be dropped and one run of all-zero groups can be replaced by two colons, so the example becomes 2001:db8::1.
A typical LAN subnet is a /64. There is no broadcast in IPv6; multicast is used instead. The ARP protocol is replaced by the Neighbor Discovery Protocol (NDP). Addresses beginning with fe80::/10 are link-local and exist on every IPv6 interface. Addresses in 2000::/3 are global unicast. fc00::/7 is unique local, similar in purpose to private IPv4.

## Layers: OSI and TCP/IP in practice
The OSI model has 7 layers: physical, data link, network, transport, session, presentation, application. The TCP/IP model groups these into 4: link, internet, transport, application.
Useful mapping: Ethernet frames and MAC addresses are layer 2. IP packets and routers are layer 3. TCP segments and UDP datagrams are layer 4. HTTP, DNS, SMTP and TLS belong to the application side.
A switch forwards frames using MAC addresses and builds a MAC address table by learning the source address of frames it sees. A router forwards packets between networks using a routing table and the longest prefix match rule: when several routes match a destination, the most specific one (longest prefix) wins.
Hubs are obsolete. A hub repeats every signal to all ports, while a switch sends a frame only to the port where the destination MAC was learned.

## ARP
On an IPv4 Ethernet LAN, a host that knows the destination IP address but not its MAC address sends an ARP request as a broadcast: who has this IP. The owner replies with its MAC address. Hosts cache the answer for a short time. If the destination is on another network, the host ARPs for the default gateway instead, not for the remote host.
ARP has no authentication, which is why ARP spoofing (also called ARP poisoning) is possible on a LAN. Dynamic ARP inspection on managed switches is one defence.

## DHCP
DHCP gives hosts an IP address, mask, default gateway, DNS servers and a lease time. The four messages are DORA: Discover (broadcast from client), Offer (from server), Request (client asks for the offered address), Acknowledge (server confirms).
Clients use UDP port 68 and servers use UDP port 67. A lease is renewed when about half of the lease time has passed. Two DHCP servers on the same LAN without coordination is a common cause of random address conflicts.

## DNS in detail
DNS maps names to records. Common record types: A (name to IPv4), AAAA (name to IPv6), CNAME (alias to another name), MX (mail servers with priority), NS (authoritative name servers), TXT (free text, used for SPF, DKIM and domain verification), PTR (reverse lookup from IP to name), SOA (zone authority information).
Resolution path when you type a name: the application asks the stub resolver of the operating system, which asks a recursive resolver (your ISP, or a public one). If the answer is not cached, the recursive resolver asks a root server, which points to the TLD servers (for example .com), which point to the authoritative servers of the domain, which return the answer. Every answer carries a TTL that says how long it may be cached.
DNS uses UDP port 53 for most queries and TCP port 53 for large responses and zone transfers. DNS over HTTPS and DNS over TLS encrypt queries between the client and the resolver.
When a DNS change seems not to work, the usual reason is caching of the old record until its TTL expires. Lowering the TTL before a planned migration is standard practice.

## TCP in detail
TCP provides a reliable, ordered byte stream. Connection setup is the three-way handshake: SYN from the client, SYN-ACK from the server, ACK from the client. Sequence numbers number the bytes, acknowledgements confirm them, and lost segments are retransmitted after a timeout or after duplicate acknowledgements.
Flow control uses the receiver window: the receiver tells the sender how much data it can buffer. Congestion control (slow start, congestion avoidance, fast retransmit) prevents the sender from overloading the network. The effective sending rate is limited by the smaller of the congestion window and the receiver window.
Closing a connection uses FIN and ACK in each direction. The side that closes first enters TIME_WAIT for a while so that late packets from the old connection are not mixed into a new one. Many sockets in TIME_WAIT on a busy server are normal. Many sockets stuck in CLOSE_WAIT usually mean the application forgot to close its side.
Common TCP flags: SYN start a connection, ACK acknowledge, FIN finish, RST abort immediately, PSH push data to the application.

## UDP and when to use it
UDP has no connection, no ordering, no retransmission and no congestion control. It is a thin layer on top of IP that adds ports and a checksum. It is used when low latency matters more than perfect delivery or when the application handles reliability itself: DNS queries, DHCP, VoIP, online games, video calls, and QUIC (the transport under HTTP/3).

## Well-known ports
20 and 21 FTP, 22 SSH, 23 Telnet (insecure), 25 SMTP, 53 DNS, 67 and 68 DHCP, 80 HTTP, 110 POP3, 123 NTP, 143 IMAP, 161 SNMP, 389 LDAP, 443 HTTPS, 445 SMB, 587 SMTP submission, 993 IMAPS, 3306 MySQL, 3389 RDP, 5432 PostgreSQL, 6379 Redis, 8080 alternative HTTP, 27017 MongoDB.
Ports 0 to 1023 are well-known ports, 1024 to 49151 are registered, and 49152 to 65535 are dynamic ports used as temporary source ports by clients.

## HTTP versions
HTTP/1.1 reuses TCP connections (keep-alive) but handles requests on a connection one after another, which causes head-of-line blocking. HTTP/2 multiplexes many streams over one TCP connection and compresses headers. HTTP/3 runs over QUIC on UDP, which removes TCP-level head-of-line blocking and speeds up connection setup.
HTTPS means HTTP carried inside TLS. TLS 1.3 completes its handshake in one round trip and removes old insecure options. The server proves its identity with a certificate signed by a certificate authority that the client trusts.

## ICMP, ping and traceroute
ICMP carries control and error messages. Ping sends ICMP echo request and waits for echo reply, and it measures round-trip time and packet loss. Traceroute sends packets with TTL values 1, 2, 3 and so on. Each router decrements the TTL, and the router where it reaches zero returns an ICMP time exceeded message, which reveals the path hop by hop. Some routers do not answer, so stars in the output do not always mean a problem.
Ping failing does not prove a host is down, because firewalls often block ICMP.

## MTU and fragmentation
Ethernet usually has an MTU (maximum transmission unit) of 1500 bytes. If a packet is bigger than the MTU of a link, it must be fragmented (IPv4) or the sender must reduce its size using path MTU discovery. Tunnels such as VPNs add headers, so a wrong MTU is a classic cause of "small requests work but large ones hang".

## VLANs
A VLAN splits one physical switch into several logical layer-2 networks. Frames are tagged with IEEE 802.1Q. A trunk port carries several VLANs, an access port carries one. Hosts in different VLANs need a router (or a layer-3 switch) to talk to each other, which is also where access control between them can be applied.

## Routing
Static routes are entered by hand. Dynamic routing protocols exchange routes automatically. RIP is a simple distance-vector protocol with a maximum of 15 hops. OSPF is a link-state protocol used inside an organisation and computes shortest paths with Dijkstra's algorithm. BGP is the path-vector protocol that connects autonomous systems and holds the internet together.
The default route 0.0.0.0/0 matches anything not matched by a more specific route and usually points to the ISP.

## Wi-Fi basics
Wi-Fi is IEEE 802.11. The 2.4 GHz band reaches further but has few non-overlapping channels (1, 6 and 11 in most regions) and more interference. The 5 GHz band is faster with more channels and shorter range. Wi-Fi 6 is 802.11ax. For security use WPA2 or WPA3 and avoid WEP and open networks. WPS push-button or PIN setup has known weaknesses.

## Load balancers, proxies, CDN
A forward proxy acts for clients. A reverse proxy sits in front of servers, and can terminate TLS, cache, compress and route requests. A load balancer spreads requests over several servers using strategies such as round robin, least connections or hashing, and removes unhealthy servers using health checks. A CDN stores copies of content in many locations so users fetch it from a nearby server.

## Troubleshooting method
Work from the bottom up or divide and conquer. First check the cable or Wi-Fi link, then the IP address and gateway, then reachability of the gateway, then reachability of an outside IP such as 8.8.8.8, then DNS by resolving a name. If an IP works but a name does not, the problem is DNS. If the name resolves but the web page does not load, test the port with curl or telnet-style tools and look at firewalls and the service itself.
Useful commands: on Windows ipconfig /all, ping, tracert, nslookup, netstat -ano. On Linux ip addr, ip route, ping, traceroute or mtr, dig, ss -tuln, curl -v. Wireshark and tcpdump show actual packets for deeper analysis.

## Firewalls and VPNs
A stateless packet filter judges each packet alone. A stateful firewall tracks connections, so replies to allowed outbound connections are allowed automatically. The default policy should be deny, with explicit allows for needed traffic. A VPN builds an encrypted tunnel between a device and a network, using protocols like WireGuard, OpenVPN or IPsec. A VPN protects traffic between you and the VPN endpoint, it does not make you anonymous.
