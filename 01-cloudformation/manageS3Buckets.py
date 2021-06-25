#!/usr/bin/env python3

import argparse
from logging import exception
import boto3, botocore.exceptions
import datetime
import cfnyaml, json, yaml
import os, pathlib, sys
from typing import NoReturn, Union, Any

# appending the path so that packages can be imported from a parent level
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from utils.pyColors import MinStyle as clr

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
def errMessage(err: botocore.exceptions.ClientError, attemptedAction: str) -> Union[None,NoReturn]:
    err_msg=err.response['Error']['Message']
    err_code=err.response['Error']['Code']
    err_http_status_code=err.response['ResponseMetadata']['HTTPStatusCode']
    if err_msg == 'No updates are to be performed.':
        print("No changes made")
        return None
    else:
        print(f'\n{clr.LIGHTRED}Encountered Unexpected error:{clr.RESET}')
        print(f'{clr.LIGHTCYAN}Attempted Action:{clr.RESET} {attemptedAction}')
        print(f'{clr.LIGHTCYAN}HTTP Code:{clr.RESET}     {err_http_status_code}')
        print(f'{clr.LIGHTCYAN}Error Code:{clr.RESET}    {err_code}')
        print(f'{clr.LIGHTCYAN}Error Message:{clr.RESET} {err_msg}')
        print()
        if args.verbose:
            print(f'Entire Error:')
            print(f'{clr.DIV_SINGLE_LONG}{clr.RESET}')
            print(f'{err}')
        sys.exit(f'\n{clr.LIGHTRED}Exiting script{clr.RESET}\n')


def updateStackOutputFile(stackOutputFile: str, stackObject: object) -> None:
    try:
        opFile=open(stackOutputFile, "a+")
        if os.stat(stackOutputFile).st_size == 0:
            print(f'updateStackOutputFile: 0 size, initial write')
            json.dump(stackObject, opFile)
        else:
            opFile.seek(0)
            prev_stack_dict=json.load(opFile)
            prev_stack_dict.update(stackObject)
            opFile.truncate(0)
            json.dump(prev_stack_dict, opFile)
        opFile.close()
    except Exception as err:
        print(f'{err}')
        sys.exit(f'\n{clr.LIGHTRED}Exiting script{clr.RESET}\n')
    return None


def upsertStack(stack_action: str, userAwsProfile: str, region: str, fullStackName: str, stackTemplate: object, stackOutputFile: str):
    action=f'AWS CLOUDFORMATION - {stack_action}Stack'
    cf_session = boto3.Session(profile_name=(userAwsProfile))
    cf_client = cf_session.client('cloudformation', region_name=(region))
    create_waiter = cf_client.get_waiter('stack_create_complete')
    update_waiter = cf_client.get_waiter('stack_update_complete')

    # for debugging, verbose output
    if args.verbose:
        print(f'\n{clr.WHITE}Stack creation parameters{clr.RESET}')
        print(f'{clr.DIV_SINGLE_MEDIUM}{clr.RESET}')
        print(f'{clr.PINK}Stack Action ...= {clr.LIGHTCYAN}{action}{clr.RESET}')
        print(f'{clr.PINK}Stack Name .....= {clr.LIGHTCYAN}{fullStackName}{clr.RESET}')
        print(f'{clr.PINK}Stack Template .= {clr.LIGHTCYAN}{stackTemplate}{clr.RESET}')
        print(f'{clr.PINK}Region .........= {clr.LIGHTCYAN}{region}{clr.RESET}')
        print()

    print(f'Attempting to {stack_action} S3 bucket in region: {region} ...', end='')
    try:
        if stack_action == 'create':
            stack_id = cf_client.create_stack(
                StackName=f'{fullStackName}',
                TemplateBody=(stackTemplate),
                DisableRollback=True,
                TimeoutInMinutes=3,
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            create_waiter.wait(
                StackName=f'{stack_id}'
            )
        else:
            stack_id = cf_client.update_stack(
                StackName=f'{fullStackName}',
                TemplateBody=(stackTemplate),
                DisableRollback=True,
                TimeoutInMinutes=3,
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            update_waiter.wait(
                StackName=f'{stack_id}'
            )
        # print success message
        print(f'  {clr.LIGHTGREEN}Success!!\n{clr.RESET}{stack_action}d Stack Id: {clr.LIGHTGREY}{stack_id["StackId"]}{clr.RESET}\n')
        # add stack Id to stack output file
        stack_dict={f'{region}': f'{stack_id["StackId"]}'}
        updateStackOutputFile(stackOutputFile, stack_dict)
        return stack_id
    except botocore.exceptions.ClientError as err:
        return errMessage(err, action)


def deleteStack(userAwsProfile: str, region: str, stackId: str) -> Union[bool,None]:
    '''
    deleteStack deletes a specified stack in a given region

    Args:
        userAwsProfile (str): The users aws credentials profile for aws programmatic access
        region (str): AWS region that the stack is in
        stackId (str): The AWS unique stack ID (the arn id)

    Returns:
        Union[bool,None]: Returns true if successful or none if an error was encountered
    '''
    action='AWS CLOUDFORMATION - DeleteStack'
    cf_client = boto3.Session(profile_name=(userAwsProfile), region_name=(region))
    cf_client = cf_client.client('cloudformation')
    waiter = cf_client.get_waiter('stack_delete_complete')

    # for debugging, verbose output
    if args.verbose:
        print(f'\n{clr.WHITE}Stack deletion parameters{clr.RESET}')
        print(f'{clr.DIV_SINGLE_MEDIUM}{clr.RESET}')
        print(f'{clr.PINK}Stack Id ..= {clr.LIGHTCYAN}{stackId}{clr.RESET}')
        print(f'{clr.PINK}Region ....= {clr.LIGHTCYAN}{region}{clr.RESET}')
        print()

    print(f'Attempting to delete S3 bucket in region: {clr.LIGHTBLUE}{region}{clr.RESET} ...', end='')
    try:
        cf_client.delete_stack(
            StackName=f'{stackId}'
        )
        waiter.wait(
            StackName=f'{stackId}'
        )
        print(f'  {clr.LIGHTGREEN}Success!!\n{clr.RESET}Deleted Stack Id: {clr.LIGHTGREY}{region_stack_id}{clr.RESET}\n')
        return True
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

# creating logfile and s3_stack_output (if create or update) files
rawDT = datetime.datetime.now()
fmtDateTime = rawDT.strftime("%Y")+"-"+rawDT.strftime("%m")+"-"+rawDT.strftime("%d")+"_"+rawDT.strftime("%H")+"_"+rawDT.strftime("%M")+"_"+rawDT.strftime("%S")
log_file=f'{pathlib.PurePath(os.path.basename(__file__)).stem}-{fmtDateTime}.txt'
stack_ouput_file=f's3-buckets-{fmtDateTime}.json'

# for debugging, verbose output of cli arguments and initial variables
if args.verbose:
    print(f'\n{clr.WHITE}Passed in arguments{clr.RESET}\n{clr.DIV_SINGLE_MEDIUM}{clr.RESET}')
    print(f'{clr.PINK}s3_stack_action : {clr.LIGHTCYAN}{s3_stack_action}{clr.RESET}')
    print(f'{clr.PINK}country ....... : {clr.LIGHTCYAN}{country}{clr.RESET}')
    print(f'{clr.PINK}stack_name .... : {clr.LIGHTCYAN}{stack_name}{clr.RESET}')
    print(f'{clr.PINK}raw_regions_file .. : {clr.LIGHTCYAN}{raw_regions_file}{clr.RESET}')
    print(f'{clr.PINK}raw_stack_template. : {clr.LIGHTCYAN}{raw_stack_template}{clr.RESET}')
    print(f'{clr.PINK}user_aws_profile: {clr.LIGHTCYAN}{user_aws_profile}{clr.RESET}')
    print(f'\n{clr.WHITE}Output files and variables{clr.RESET}\n{clr.DIV_SINGLE_MEDIUM}{clr.RESET}')
    print(f'{clr.PINK}fmtDateTime: {clr.LIGHTCYAN}{fmtDateTime}{clr.RESET}')
    print(f'{clr.PINK}log_file: {clr.LIGHTCYAN}{log_file}{clr.RESET}')
    print(f'{clr.PINK}stack_ouput_file: {clr.LIGHTCYAN}{stack_ouput_file}{clr.RESET}')

all_regions = yaml.safe_load(raw_regions_file)
country_regions = all_regions[(country)]
stack_ids = []
stack_template = ''
if s3_stack_action == 'delete':
    stack_ids = json.load(raw_stack_template)
else:
    stack_temp = cfnyaml.load(raw_stack_template)
    stack_template = cfnyaml.dump(stack_temp)


# for debugging, verbose output of transformed data values
if args.verbose:
    print(f'\n{clr.WHITE}Regions in Country{clr.RESET}')
    print(f'{clr.DIV_SINGLE_MEDIUM}{clr.RESET}')
    print(f'{clr.PINK}country_regions= {clr.LIGHTCYAN}{country_regions}{clr.RESET}\n')

if (args.verbose and s3_stack_action == 'create'):
    print(f'\n{clr.WHITE}Stack Template{clr.RESET}')
    print(f'{clr.DIV_SINGLE_MEDIUM}{clr.RESET}')
    print(f'{clr.PINK}stack_template= {clr.LIGHTCYAN}{stack_template}{clr.RESET}\n')

if (args.verbose and s3_stack_action == 'delete'):
    print(f'\n{clr.WHITE}Stack Ids{clr.RESET}')
    print(f'{clr.DIV_SINGLE_MEDIUM}{clr.RESET}')
    print(f'{clr.PINK}stack_ids= {clr.LIGHTCYAN}{stack_ids}{clr.RESET}\n')

print()
for region in country_regions:
    full_stack_name=f'{stack_name}-{region}'
    if s3_stack_action == 'delete':
        region_stack_id = stack_ids[(region)]
        response = deleteStack(user_aws_profile, region, region_stack_id)
    else:
        response = upsertStack(s3_stack_action, user_aws_profile, region, full_stack_name, stack_template, stack_ouput_file)
        print(f'{full_stack_name}\'s StackId= {response["StackId"]}\n')
