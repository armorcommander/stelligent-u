#!/usr/bin/env python3

import argparse
import boto3
from botocore.compat import total_seconds
import yaml
import os
import sys


# appending the path so that packages can be imported from a parent level
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from utils.pyColors import MinStyle

# create the commandline parser
my_parser = argparse.ArgumentParser(prog='manageS3Buckets',
                                    usage='%(prog)s [-h] country stack_action stack_name regions_file',
                                    description='Create, update or delete an s3 stack in all regions for a given country')

my_parser.add_argument('country',
                       metavar='country',
                       type=str,
                       choices=['usa', 'eu'],
                       help='Indicates which country\'s regions the s3 buckets will be created in. Options are one of [ create, update, delete ]')

# adding cli arguments
my_parser.add_argument('stack_action',
                       metavar='stack_action',
                       type=str,
                       choices=['create', 'update', 'delete'],
                       help='Indicates what action is to be taken. Options are one of [ create, update, delete ]')

my_parser.add_argument('stack_name',
                       metavar='stack_name',
                       type=str,
                       help='A custom name for the s3 bucket. It will be incorporated in all regions as \'<current_aws_region>-<stack_name>\'')

my_parser.add_argument('regions_file',
                       metavar='regions_file',
                       type=argparse.FileType('r'),
                       help='A yaml config file containing the countries and their regions')

my_parser.add_argument('--verbose',
                       help='Increases output verbosity',
                       action='store_true'
                       )

# execute the parse_args() method
args = my_parser.parse_args()

# assigning the input args
country = args.country
s3_stack_action = args.stack_action
stack_name = args.stack_name
regions_file = args.regions_file

if args.verbose:
    print(f'\n{MinStyle.WHITE}Passed in arguments{MinStyle.RESET}')
    print(f'{MinStyle.WHITE}----------------------------------------------{MinStyle.RESET}')
    print(f'{MinStyle.PINK}country: {MinStyle.LIGHTCYAN}{country}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}s3_stack_action: {MinStyle.LIGHTCYAN}{s3_stack_action}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}stack_name: {MinStyle.LIGHTCYAN}{stack_name}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}regions_file: {MinStyle.LIGHTCYAN}{regions_file}{MinStyle.RESET}\n')

all_regions = yaml.safe_load(regions_file)
country_regions = all_regions[(country)]

if args.verbose:
    print(f'\n{MinStyle.WHITE}Regions in Country{MinStyle.RESET}')
    print(f'{MinStyle.WHITE}----------------------------------------------{MinStyle.RESET}')
    print(f'{MinStyle.PINK}country_regions= {MinStyle.LIGHTCYAN}{country_regions}{MinStyle.RESET}\n')



for region in country_regions:
    s3_session = boto3.Session(profile_name='st_mfa_creds')
    s3_client = s3_session.client('cloudformation', region_name=(region))
    # TODO
    # - print out attempting message
    # - create stack
    # - wait for stack completion
    # - print success/failure message
    print(f'region={region}')
