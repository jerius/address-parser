#!/usr/bin/env python

import logging
import sys
import argparse
import re
import pdb
import usaddress
from pygeocoder import Geocoder

# CLI Arguments
parser = argparse.ArgumentParser(description='Parse an address list into LLS format CSV')
parser.add_argument('--address_file', action='store', dest='address_file',
                    help='The text file containing the addresses to parse', required='True')
args = parser.parse_args()

# Logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)


def addr_chunks_from_file(addr_file):
    file = open(addr_file)
    file_contents = file.read()
    addr_chunks = re.sub(r'\n\s*\n', '\n\n', file_contents).split("\n\n")

    return addr_chunks


def construct_mail_address(tagged_address):
    if tagged_address[1] == 'Street Address':
        normalized_addr = ', '.join([f'{value}' for key, value in tagged_address[0].items()])
    elif tagged_address[1] == 'Ambiguous':
        logging.debug("Error: Invalid address.")
        logging.debug(tagged_address)
        normalized_addr = "Invalid Address"
    else:
        logging.debug(f"Error: Not a street address. ({tagged_address[1]})")
        logging.debug(tagged_address)
        normalized_addr = "Invalid Address"

    return normalized_addr


def extract_mailing_address(address):
    try:
        tagged_address = usaddress.tag(address)
        return tagged_address
    except usaddress.RepeatedLabelError as e:
        print(e.parsed_string)
        return {}


def validate_address(self, mail_address):
    return None


def parse_addrs(addr_chunks):
    for chunk in addr_chunks:
        chunk_split = chunk.splitlines()
        name = chunk_split[0]
        addr = ' '.join(chunk_split[1:])
        parsed_addr = extract_mailing_address(addr)
        normalized_addr = construct_mail_address(parsed_addr)
        # pdb.set_trace()
        print(f"NAME: {name}")
        print(f"ADDR: {normalized_addr}")
        print('')


Addr_Chunks = addr_chunks_from_file(args.address_file)

parse_addrs(Addr_Chunks)