#!/usr/bin/env python

import logging
import sys
import os
import argparse
import re
import pdb
import usaddress
from pygeocoder import Geocoder
from pygeolib import GeocoderError
import urllib.parse

# CLI Arguments
parser = argparse.ArgumentParser(description='Parse an address list into LLS format CSV')
parser.add_argument('--address_file', action='store', dest='address_file',
                    help='The text file containing the addresses to parse', required='True')
args = parser.parse_args()

# Required Env Var
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if GOOGLE_API_KEY is None:
    print(f"Error: 'GOOGLE_API_KEY' required in environment. Please export and try again.")
    sys.exit(1)

# Logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)


def addr_chunks_from_file(addr_file):
    file = open(addr_file)
    file_contents = file.read()
    addr_chunks = re.sub(r'\n\s*\n', '\n\n', file_contents).split("\n\n")

    return addr_chunks


def url_encode(addr):
    safe_string = urllib.parse.quote_plus(addr)

    return safe_string


def valid_address(addr):
    address = Geocoder(GOOGLE_API_KEY).geocode(urllib.parse.quote_plus(addr))
    status = address.valid_address

    return status


def normalize_address(addr):
    address = Geocoder(GOOGLE_API_KEY).geocode(urllib.parse.quote_plus(addr))
    normalized_addr = address.formatted_address

    return normalized_addr


def extract_mailing_address(addr):
    try:
        tagged_address = usaddress.tag(addr)
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
        try:
            address = Geocoder(GOOGLE_API_KEY).geocode(addr)
        except GeocoderError:
            print(f"The address entered could not be geocoded")
            sys.exit(1)

        print(address)
        # parsed_addr = extract_mailing_address(addr)
        valid = address.valid_address
        if valid:
            normalized_address = address.formatted_address
        else:
            normalized_address = "Invalid address."

        print(f"NAME: {name}")
        print(f"ADDR: {normalized_address}")
        print('')
        sys.exit(0)


Addr_Chunks = addr_chunks_from_file(args.address_file)

parse_addrs(Addr_Chunks)