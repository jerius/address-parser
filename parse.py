#!/usr/bin/env python

import sys
import os
import argparse
import re
import usaddress
import csv

from pygeocoder import Geocoder
from pygeolib import GeocoderError

# CLI Arguments
parser = argparse.ArgumentParser(description='Parse addresses CSV')
parser.add_argument('--address_file', action='store', dest='address_file',
                    help='The text file containing the addresses to parse',
                    required='True')
args = parser.parse_args()

# Required Env Var
API_KEY = os.getenv('GOOGLE_API_KEY')

if API_KEY is None:
    print(f"Error: 'GOOGLE_API_KEY' required in environment. Please export and\
           try again.")
    sys.exit(1)

# METHODS


def addr_chunks_from_file(addr_file):
    file = open(addr_file)
    file_contents = file.read()
    addr_chunks = re.sub(r'\n\s*\n', '\n\n', file_contents).split("\n\n")

    return addr_chunks


def extract_mailing_address(addr):
    try:
        tagged_address = usaddress.tag(addr)
        return tagged_address
    except usaddress.RepeatedLabelError as e:
        print(e.parsed_string)
        return {}


def parse_addrs(addr_chunks):
    for chunk in addr_chunks:
        chunk_split = chunk.splitlines()
        name = chunk_split[0]
        addr = ' '.join(chunk_split[1:])
        if addr:
            try:
                address = Geocoder(API_KEY).geocode(addr)
                normalized_address = extract_mailing_address(
                    address.formatted_address)
            except GeocoderError:
                normalized_address = "Invalid"
        else:
            normalized_address = None

        # TODO: parse normalized address into hash
        data = [name, normalized_address[0]['Address']]
        with open('countries.csv', 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerow(data)


# EXECUTE

header = ['First Name (s) **', 'Last Name **', 'Street Address **',
          'Address Line 2 **', 'City **', 'State **', 'Zip **', 'Country **']

Addr_Chunks = addr_chunks_from_file(args.address_file)
parse_addrs(Addr_Chunks)
