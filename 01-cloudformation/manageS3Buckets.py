#!/usr/bin/env python3

import argparse
import boto3
import botocore.exceptions
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
    s3_session = boto3.Session(profile_name=(userAwsProfile))
    s3_client = s3_session.client('cloudformation', region_name=(region))

    if args.verbose:
        print(f'\n{MinStyle.WHITE}Stack creation parameters{MinStyle.RESET}')
        print(f'{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Stack Name ... = {MinStyle.LIGHTCYAN}{fullStackName}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Stack Template = {MinStyle.LIGHTCYAN}{stackTemplate}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Region ....... = {MinStyle.LIGHTCYAN}{region}{MinStyle.RESET}')
        print()

    print(f'Attempting to create S3 bucket in region: {region}')
    try:
        s3_client_response = s3_client.create_stack(
            StackName=f'{full_stack_name}',
            TemplateBody=f'{stack_template}',
            DisableRollback=True,
            TimeoutInMinutes=3,
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
    except s3_client.exceptions.LimitExceededException as err:
        errMessage(err, action)
    except s3_client.exceptions.AlreadyExistsException as err:
        errMessage(err, action)
    except s3_client.exceptions.TokenAlreadyExistsException as err:
        errMessage(err, action)
    except s3_client.exceptions.InsufficientCapabilitiesException as err:
        errMessage(err, action)
    except botocore.exceptions.ClientError as err:
        errMessage(err, action)
    else:
        return s3_client_response


def updateStack(userAwsProfile, region, fullStackName, stackTemplate):
    action='AWS CLOUDFORMATION - UpdateStack'
    s3_session = boto3.Session(profile_name=(userAwsProfile))
    s3_client = s3_session.client('cloudformation', region_name=(region))

    if args.verbose:
        print(f'\n{MinStyle.WHITE}Stack creation parameters{MinStyle.RESET}')
        print(f'{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Stack Name ... = {MinStyle.LIGHTCYAN}{fullStackName}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Stack Template = {MinStyle.LIGHTCYAN}{stackTemplate}{MinStyle.RESET}')
        print(f'{MinStyle.PINK}Region ....... = {MinStyle.LIGHTCYAN}{region}{MinStyle.RESET}')
        print()

    print(f'Attempting to create S3 bucket in region: {region}')
    try:
        s3_client_response = s3_client.update_stack(
            StackName=f'{full_stack_name}',
            TemplateBody=f'{stack_template}',
            DisableRollback=True,
            TimeoutInMinutes=3,
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
    except s3_client.exceptions.LimitExceededException as err:
        errMessage(err, action)
    except s3_client.exceptions.AlreadyExistsException as err:
        errMessage(err, action)
    except s3_client.exceptions.TokenAlreadyExistsException as err:
        errMessage(err, action)
    except s3_client.exceptions.InsufficientCapabilitiesException as err:
        errMessage(err, action)
    except botocore.exceptions.ClientError as err:
        errMessage(err, action)
    else:
        return s3_client_response

# execute the parse_args() method
args = my_parser.parse_args()

# assigning the input args
s3_stack_action = args.stack_action
country = args.country
stack_name = args.stack_name
regions_file = args.regions_file
stack_template = args.stack_template
user_aws_profile = args.user_aws_profile

if args.verbose:
    print(f'\n{MinStyle.WHITE}Passed in arguments{MinStyle.RESET}')
    print(f'{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}s3_stack_action : {MinStyle.LIGHTCYAN}{s3_stack_action}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}country ....... : {MinStyle.LIGHTCYAN}{country}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}stack_name .... : {MinStyle.LIGHTCYAN}{stack_name}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}regions_file .. : {MinStyle.LIGHTCYAN}{regions_file}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}stack_template. : {MinStyle.LIGHTCYAN}{stack_template}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}user_aws_profile: {MinStyle.LIGHTCYAN}{user_aws_profile}{MinStyle.RESET}\n')

all_regions = yaml.safe_load(regions_file)
country_regions = all_regions[(country)]

if args.verbose:
    print(f'\n{MinStyle.WHITE}Regions in Country{MinStyle.RESET}')
    print(f'{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
    print(f'{MinStyle.PINK}country_regions= {MinStyle.LIGHTCYAN}{country_regions}{MinStyle.RESET}\n')


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
        response = createStack(user_aws_profile, region, full_stack_name, stack_template)
        print(f'{full_stack_name}\'s StackId= {response["StackId"]}\n')
