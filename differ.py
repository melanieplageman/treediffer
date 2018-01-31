#! /usr/bin/env python3

import atexit
import docker
import json
import psycopg2
import re
import sys

init_regex = re.compile(b'PostgreSQL init process complete; ready for start up.')
accept_regex = re.compile(b'database system is ready to accept connections')

POSTGRESQL_PORT = '5432/tcp'

client = docker.from_env()
try:
    container_1 = client.containers.run("postgres:alpine", detach=True, ports={POSTGRESQL_PORT: None})
    atexit.register(container_1.kill)
except docker.errors.APIError as e:
    print("image not found %s" % e)

# try:
#     container_2 = client.containers.run("postgres:alpine", detach=True, ports={POSTGRESQL_PORT: None})
#     atexit.register(container_2.kill)
# except docker.errors.APIError as e:
#     print("image not found %s" % e)

print('Reloading container 1', file=sys.stderr)
container_1.reload()

# print('Reloading container 2', file=sys.stderr)
# container_2.reload()

port_1 = container_1.attrs['NetworkSettings']['Ports'][POSTGRESQL_PORT][0]['HostPort']
# port_2 = container_2.attrs['NetworkSettings']['Ports'][POSTGRESQL_PORT][0]['HostPort']

stream = container_1.attach(stderr=True, stream=True)

for i in stream:
    if init_regex.search(i): break

for i in stream:
    if accept_regex.search(i): break

print('Establishing connection to PostgreSQL on container 1', file=sys.stderr)
connection_1 = psycopg2.connect(host='localhost', dbname='postgres', user='postgres', port=port_1)
# connection_2 = psycopg2.connect(host='localhost', dbname='postgres', user='postgres', port=port_2)

# initialized = False
# for i in container_1.attach(stderr=True, stream=True):
#     init_match = re.search(init_regex, i)
#     if init_match:
#         print(init_match.group(0))
#         initialized = True
#     if initialized:
#         accept_match = re.search(accept_regex, i)
#         if accept_match:
#             print(accept_match.group(0))

#             print('Establishing connection to PostgreSQL on container 1', file=sys.stderr)
#             connection_1 = psycopg2.connect(host='localhost', dbname='postgres', user='postgres', port=port_1)
#             # connection_2 = psycopg2.connect(host='localhost', dbname='postgres', user='postgres', port=port_2)
