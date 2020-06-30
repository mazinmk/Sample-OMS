import random
import socket
import struct

# Generate random ipaddress and convert into json format
# This is used to populate fraud_ip mongodb metastore
for i in range(500):
    ip_json_format = "{{\"ip_address\":\"{0}\"}}"
    random_ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
    print(ip_json_format.format(random_ip))


    
