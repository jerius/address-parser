#!/usr/bin/env python

# TODO: Parsing names better.
# ie "Joe and Rachel Smith", or "Joe Smith and Rachel Black"
# Need to handle both varieties along with "The Smiths"

import sys
import os
import argparse
import re
import usaddress
import csvkit
import pdb

from collections import OrderedDict
from nameparser import HumanName
from pygeocoder import Geocoder
from pygeolib import GeocoderError

# CLI Arguments
parser = argparse.ArgumentParser(description='Parse addresses CSV')
parser.add_argument('--address_file', action='store', dest='address_file',
                    help='The text file containing the addresses to parse',
                    required='True')
parser.add_argument('--team_member', action='store', dest='team_member',
                    help='The team member associated with these addresses',
                    required='True')
args = parser.parse_args()

# Required Env Var
API_KEY = os.getenv('GOOGLE_API_KEY')

if API_KEY is None:
    print("Error: 'GOOGLE_API_KEY' required in environment. Please export and try again.")
    sys.exit(1)

# METHODS


def addr_chunks_from_file(addr_file):
    file = open(addr_file)
    file_contents = file.read()
    file.close
    addr_chunks = re.sub(r'\n\s*\n', '\n\n', file_contents).split("\n\n")

    return addr_chunks


def extract_mailing_address(addr):
    try:
        tagged_address = usaddress.tag(addr)
        return tagged_address
    except usaddress.RepeatedLabelError as e:
        print(e.parsed_string)
        return {}


def parse_addrs(addr_chunks, csv_header):
    all_addresses = []
    for chunk in addr_chunks:
        chunk_split = chunk.splitlines()
        name = HumanName(chunk_split[0])
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

        if normalized_address:
            addr_type = normalized_address[1]
            if addr_type == 'Street Address':
                addr_copy = normalized_address[0].copy()
                addr_copy['FirstName'] = name.first
                addr_copy['LastName'] = name.last.capitalize()
                all_addresses.append(addr_copy)
        else:
            nd = {}
            nd['FirstName'] = name.first.capitalize()
            nd['LastName'] = name.last.capitalize()
            all_addresses.append(nd)

    return all_addresses


# EXECUTE

csv_header = ['First Name (s) **', 'Last Name **', 'Street Address **',
              'Address Line 2 **', 'City **', 'State **', 'Zip **',
              'Country **']

member = args.team_member.replace(" ", "_").lower()

Addr_Chunks = addr_chunks_from_file(args.address_file)
full_list = parse_addrs(Addr_Chunks, csv_header)

all_rows = []

for address in full_list:
    od = OrderedDict()
    od['First Name (s) **'] = address.get('FirstName')
    od['Last Name **'] = address.get('LastName')
    street_address = []
    for k, v in address.items():
        keys = ['AddressNumber', 'StreetNamePreDirectional', 'StreetName',
                'StreetNamePostType', 'OccupancyIdentifier']
        if k in keys:
            street_address.append(v)
    od['Street Address **'] = ' '.join(street_address)
    od['City **'] = address.get('PlaceName')
    od['State **'] = address.get('StateName')
    od['Zip **'] = address.get('ZipCode')
    od['Country **'] = address.get('CountryName')
    all_rows.append(od)

with open(member + '.csv', 'w') as outfile:
    writer = csvkit.DictWriter(outfile, csv_header)
    writer.writeheader()
    writer.writerows(all_rows)
