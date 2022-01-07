#!/usr/bin/env python

import sys
import os
import argparse
import re
import usaddress
import csvkit
import pdb

from collections import OrderedDict
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
    print(f"Error: 'GOOGLE_API_KEY' required in environment. Please export and try again.")
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


def parse_addrs(addr_chunks, csv_header):
    all_addresses = []
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

        if normalized_address:
            addr_type = normalized_address[1]
            if addr_type == 'Street Address':
                addr_copy = normalized_address[0].copy()
                addr_copy['Name'] = name
                all_addresses.append(addr_copy)
        else:
            nd = {}
            nd['Name'] = name
            nd['AddressNumber'] = 'n/a'
            all_addresses.append(nd)

    return all_addresses


# EXECUTE

# csv_header = ['First Name (s) **', 'Last Name **', 'Street Address **',
#               'Address Line 2 **', 'City **', 'State **', 'Zip **',
#               'Country **']

csv_header = ['Name', 'StreetAddress', 'City', 'State', 'Zip', 'Country']

addr_field_list = ['AddressNumber', 'AddressNumberPrefix',
              'AddressNumberSuffix', 'BuildingName', 'CornerOf',
              'IntersectionSeparator', 'LandmarkName', 'NotAddress',
              'OccupancyType', 'OccupancyIdentifier', 'PlaceName',
              'Recipient', 'StateName', 'StreetName',
              'StreetNamePreDirectional', 'StreetNamePreModifier',
              'StreetNamePreType', 'StreetNamePostDirectional',
              'StreetNamePostModifier', 'StreetNamePostType',
              'SubaddressIdentifier', 'SubaddressType', 'USPSBoxGroupID',
              'USPSBoxGroupType', 'USPSBoxID', 'USPSBoxType', 'ZipCode',
              'CountryName']

Addr_Chunks = addr_chunks_from_file(args.address_file)
full_list = parse_addrs(Addr_Chunks, csv_header)

all_rows = []

for address in full_list:
    od = OrderedDict()
    od['Name'] = address['Name']
    street_address = []
    for k, v in address.items():
        keys = ['AddressNumber', 'StreetNamePreDirectional', 'StreetName',
                'StreetNamePostType', 'OccupancyIdentifier']
        if k in keys:
            street_address.append(v)
    od['StreetAddress'] = ' '.join(street_address)
    od['City'] = address.get('PlaceName')
    od['State'] = address.get('StateName')
    od['Zip'] = address.get('ZipCode')
    od['Country'] = address.get('CountryName')
    all_rows.append(od)

with open('test.csv', 'w') as outfile:
    writer = csvkit.DictWriter(outfile, csv_header)
    writer.writeheader()
    writer.writerows(all_rows)
