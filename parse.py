#!/usr/bin/env python

import re
import pdb
import usaddress

addr_file = "addresses.txt"

file = open(addr_file)
file_contents = file.read()
addr_chunks = re.sub(r'\n\s*\n', '\n\n', file_contents).split("\n\n")

for chunk in addr_chunks:
    chunk_split = chunk.splitlines()
    name = chunk_split[0]
    addr = chunk_split[1:]
    # addr_oneline = addr.replace('\n', ' ')
    print(f"NAME: {name}")
    print(f"ADDR: {addr}")
    print('')