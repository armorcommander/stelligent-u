#!/usr/bin/env python3

import argparse
import boto3
import botocore.exceptions
import yaml, cfnyaml, json
import os
import sys

# appending the path so that packages can be imported from a parent level
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from utils.pyColors import MinStyle

# create the commandline parser
my_parser = argparse.ArgumentParser(prog='manageS3Buckets',
                                    usage='%(prog)s [-h] country stack_action stack_name regions_file',
                                    description='Create, update or delete an s3 stack in all regions for a given country')

# adding cli arguments
my_parser.add_argument('stack_action',
                       metavar='stack_action',
                       type=str,
                       choices=['create', 'update', 'delete'],
                       help='Indicates what action is to be taken. Options are one of [ create, update, delete ]')

my_parser.add_argument('country',
                       metavar='country',
                       type=str,
                       default='usa',
                       choices=['usa', 'eu'],
                       help='Indicates which country\'s regions the s3 buckets will be created in. Options are one of [ create, update, delete ]')

my_parser.add_argument('stack_name',
                       metavar='stack_name',
                       type=str,
                       default='mys3stack',
                       help='A custom name for the s3 bucket management stack. It will be incorporated in all regions as \'<current_aws_region>-<stack_name>\'')

my_parser.add_argument('regions_file',
                       metavar='regions_file',
                       type=argparse.FileType('r'),
                       help='A yaml config file containing the countries and their regions')

my_parser.add_argument('stack_template',
                       metavar='stack_template',
                       type=argparse.FileType('r'),
                       help='A yaml config file containing stack templet to create')

my_parser.add_argument('--user_aws_profile',
                       metavar='user_aws_profile',
                       type=str,
                       default='st_mfa_creds',
                       help='The users aws credentials profile to use for programmatic access')

my_parser.add_argument('--verbose',
                       help='Increases output verbosity',
                       action='store_true'
                       )

# internal script functions
def errMessage(err, attemptedAction):
    err_msg=err.response['Error']['Message']
    err_code=err.response['Error']['Code']
    err_http_status_code=err.response['ResponseMetadata']['HTTPStatusCode']
    if err_msg == 'No updates are to be performed.':
        print("No changes made")
        return None
    else:
        print(f'\n{MinStyle.LIGHTRED}Encountered Unexpected error:{MinStyle.RESET}')
        print(f'{MinStyle.LIGHTCYAN}Attempted Action:{MinStyle.RESET} {attemptedAction}')
        print(f'{MinStyle.LIGHTCYAN}HTTP Code:{MinStyle.RESET}     {err_http_status_code}')
        print(f'{MinStyle.LIGHTCYAN}Error Code:{MinStyle.RESET}    {err_code}')
        print(f'{MinStyle.LIGHTCYAN}Error Message:{MinStyle.RESET} {err_msg}')
        print()
        if args.verbose:
            print(f'Entire Error:')
            print(f'{MinStyle.DIV_SINGLE_LONG}{MinStyle.RESET}')
            print(f'{err}')
        sys.exit(f'\n{MinStyle.LIGHTRED}Exiting script{MinStyle.RESET}\n')


def createStack(userAwsProfile, region, fullStackName, stackTemplate):
    action='AWS CLOUDFORMATION - CreateStack'
    cf_session = boto3.Session(profile_name=(userAwsProfile))
    cf_client = cf_session.client('cloudformation', region_name=(region))

    if args.verbose:
        print(f'\n{MinStyle.WHITE}Stack creation parameters{MinStyle.RESET}')
        print(f'{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Stack Name ... = {MinStyle.LIGHTCYAN}{fullStackName}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Stack Template = {MinStyle.LIGHTCYAN}{stackTemplate}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Region ....... = {MinStyle.LIGHTCYAN}{region}{MinStyle.RESET}')
        print()

    print(f'Attempting to create S3 bucket in region: {region}')
    try:
        return cf_client.create_stack(
            StackName=f'{fullStackName}',
            TemplateBody=(stackTemplate),
            DisableRollback=True,
            TimeoutInMinutes=3,
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
    except botocore.exceptions.ClientError as err:
        return errMessage(err, action)


def updateStack(userAwsProfile, region, fullStackName, stackTemplate):
    action='AWS CLOUDFORMATION - UpdateStack'
    cf_client = boto3.Session(profile_name=(userAwsProfile))
    cf_client = cf_client.client('cloudformation', region_name=(region))

    if args.verbose:
        print(f'\n{MinStyle.WHITE}Stack update parameters{MinStyle.RESET}')
        print(f'{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Stack Name ... = {MinStyle.LIGHTCYAN}{fullStackName}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Stack Template = {MinStyle.LIGHTCYAN}{stackTemplate}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Region ....... = {MinStyle.LIGHTCYAN}{region}{MinStyle.RESET}')
        print()

    print(f'Attempting to update S3 bucket in region: {region}')
    try:
        return cf_client.update_stack(
            StackName=f'{fullStackName}',
            TemplateBody=f'{stackTemplate}',
            DisableRollback=True,
            TimeoutInMinutes=3,
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
    except botocore.exceptions.ClientError as err:
        return errMessage(err, action)

def deleteStack(userAwsProfile, region, fullStackName, stackTemplate):
    action='AWS CLOUDFORMATION - DeleteStack'
    cf_client = boto3.Session(profile_name=(userAwsProfile))
    cf_client = cf_client.client('cloudformation', region_name=(region))

    if args.verbose:
        print(f'\n{MinStyle.WHITE}Stack deletion parameters{MinStyle.RESET}')
        print(f'{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Stack Name ... = {MinStyle.LIGHTCYAN}{fullStackName}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Stack Template = {MinStyle.LIGHTCYAN}{stackTemplate}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Region ....... = {MinStyle.LIGHTCYAN}{region}{MinStyle.RESET}')
        print()

    print(f'Attempting to delete S3 bucket in region: {region}')
    try:
        return cf_client.delete_stack(
            StackName=f'{fullStackName}',
            TemplateBody=f'{stackTemplate}',
            DisableRollback=True,
            TimeoutInMinutes=3,
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
    except botocore.exceptions.ClientError as err:
        return errMessage(err, action)

# execute the parse_args() method
args = my_parser.parse_args()

# assigning the input args
s3_stack_action = args.stack_action
country = args.country
stack_name = args.stack_name
raw_regions_file = args.regions_file
raw_stack_template = args.stack_template
user_aws_profile = args.user_aws_profile

if args.verbose:
    print(f'\n{MinStyle.WHITE}Passed in arguments{MinStyle.RESET}')
    print(f'{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}s3_stack_action : {MinStyle.LIGHTCYAN}{s3_stack_action}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}country ....... : {MinStyle.LIGHTCYAN}{country}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}stack_name .... : {MinStyle.LIGHTCYAN}{stack_name}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}raw_regions_file .. : {MinStyle.LIGHTCYAN}{raw_regions_file}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}raw_stack_template. : {MinStyle.LIGHTCYAN}{raw_stack_template}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}user_aws_profile: {MinStyle.LIGHTCYAN}{user_aws_profile}{MinStyle.RESET}\n')

all_regions = yaml.safe_load(raw_regions_file)
country_regions = all_regions[(country)]
stack_ids = []
stack_template = ''
if s3_stack_action == 'delete':
    raw_stack_ids = json.load(raw_stack_template)
    stack_ids = raw_stack_ids
else:
    stack_temp = cfnyaml.load(raw_stack_template)
    # stack_temp = cfnyaml.load(open('lab131-s3.yaml'))
    stack_template = cfnyaml.dump(stack_temp)


if args.verbose:
    print(f'\n{MinStyle.WHITE}Regions in Country{MinStyle.RESET}')
    print(f'{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}country_regions= {MinStyle.LIGHTCYAN}{country_regions}{MinStyle.RESET}\n')

if (args.verbose and s3_stack_action == 'create'):
    print(f'\n{MinStyle.WHITE}Stack Template{MinStyle.RESET}')
    print(f'{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}stack_template= {MinStyle.LIGHTCYAN}{stack_template}{MinStyle.RESET}\n')

if (args.verbose and s3_stack_action == 'delete'):
    print(f'\n{MinStyle.WHITE}Stack Ids{MinStyle.RESET}')
    print(f'{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}stack_ids= {MinStyle.LIGHTCYAN}{stack_ids}{MinStyle.RESET}\n')


# TODO
# - create stack
# - wait for stack completion
# - print success/failure message
for region in country_regions:
    full_stack_name=f'{stack_name}-{region}'
    if s3_stack_action == 'create':
        response = createStack(user_aws_profile, region, full_stack_name, stack_template)
        print(f'{full_stack_name}\'s StackId= {response["StackId"]}\n')
    elif s3_stack_action == 'update':
        response = updateStack(user_aws_profile, region, full_stack_name, stack_template)
        print(f'{full_stack_name}\'s StackId= {response["StackId"]}\n')
    elif s3_stack_action == 'delete':
        response = deleteStack(user_aws_profile, region, full_stack_name, stack_template)
        # print(f'{full_stack_name}\'s StackId= {response["StackId"]}\n')
