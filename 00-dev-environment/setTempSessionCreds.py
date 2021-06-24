#!/usr/bin/env python3

# ===========================================================================================================
# Author: John Hunter    Initial creation: 14Jun2021
#
# Description:
#     This takes an input MFA token and gets a temporary session token that is used to create
#     temporary credentials for programatically accessing AWS for a limited duration
#
# Usage and Arguments:
#  - Running the script with no arguments will display the usage and arguments information
#
# ===========================================================================================================
#
# Additional TODO
#  - Validation of the MFA token (validate against definition - type, length, characters, etc)
#  - Validate duration_seconds option (type, min/max boundaries, etc)
#  - Refactor more of the code to be functions


import argparse, boto3, botocore.exceptions, configparser, os, sys

# appending the path so that packages can be imported from a parent level
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from utils.pyColors import MinStyle  # isort:skip


# create the commandline parser
my_parser = argparse.ArgumentParser(prog='setTempSessionCreds',
                                    usage='%(prog)s [-h] mfa_token',
                                    description='Use your MFA Token to create temporary credentials using a session token')

# adding cli arguments
my_parser.add_argument('mfa_token',
                       metavar='mfa_token',
                       type=str,
                       help='The MFA token used to obtain the temporary session token')

my_parser.add_argument('--base_profile',
                       type=str,
                       default='st_jh_labs',
                       help='The profile to use to obtain temporary session credits'
)

my_parser.add_argument('--tmp_profile',
                       type=str,
                       default='st_mfa_creds',
                       help='The profile to modify and update with the temporary session credits'
)

my_parser.add_argument('--aws_credentials_file',
                       type=str,
                       default='/Users/John.Hunter/.aws/credentials',
                       help='The profile to modify and update with the temporary session credits'
)

my_parser.add_argument('--mfa_arn',
                       type=str,
                       default='arn:aws:iam::324320755747:mfa/john.hunter.labs',
                       help='The MFA Token'
)

my_parser.add_argument('--duration_seconds',
                       type=int,
                       default=43200, # 12 hour duration
                       help='The duration, in seconds, that the temporary credentials should remain valid. Min=900 seconds (15 minutes), Max=129600 seconds (36 hours)'
)

my_parser.add_argument('-v', '--verbose',
                       help='Increases output verbosity',
                       action='store_true'
                       )

# setting up imported methods
args = my_parser.parse_args()
config = configparser.ConfigParser()

# internal script functions
def errMessage(errMessage, attemptedAction):
    err_msg=errMessage.response['Error']['Message']
    err_code=errMessage.response['Error']['Code']
    err_http_status_code=errMessage.response['ResponseMetadata']['HTTPStatusCode']
    print(f'\n{MinStyle.LIGHTRED}Unexpected error:{MinStyle.RESET}')
    print(f'{MinStyle.LIGHTCYAN}Attempted Action:{MinStyle.RESET} {attemptedAction}')
    print(f'{MinStyle.LIGHTCYAN}HTTP Code:{MinStyle.RESET}     {err_http_status_code}')
    print(f'{MinStyle.LIGHTCYAN}Error Code:{MinStyle.RESET}    {err_code}')
    print(f'{MinStyle.LIGHTCYAN}Error Message:{MinStyle.RESET} {err_msg}')
    sys.exit(f'\n{MinStyle.LIGHTRED}Exiting script{MinStyle.RESET}\n')
    print()

def getCallerIdentity(awsProfile):
    action='AWS STS - GetCallerIdentity'
    st_session = boto3.Session(profile_name=(awsProfile))
    st_profile_sts_client = st_session.client('sts')
    try:
        caller_identity_response = st_profile_sts_client.get_caller_identity()
        if args.verbose:
            print(f'{MinStyle.PINK}STS Caller Identity values{MinStyle.RESET}')
            print(f'{MinStyle.LIGHTGREY}{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
            print(f'{MinStyle.LIGHTCYAN}UserId: {MinStyle.WHITE}{caller_identity_response.get("UserId")}{MinStyle.RESET}')
            print(f'{MinStyle.LIGHTCYAN}Account: {MinStyle.WHITE}{caller_identity_response.get("Account")}{MinStyle.RESET}')
            print(f'{MinStyle.LIGHTCYAN}Arn: {MinStyle.WHITE}{caller_identity_response.get("Arn")}{MinStyle.RESET}')
            print()
    except botocore.exceptions.ClientError as err:
        errMessage(err, action)
    return

def getUser(awsProfile):
    action='AWS IAM - GetUser'
    iam_session = boto3.Session(profile_name=(awsProfile))
    iam_client = iam_session.client('iam')
    try:
        get_user_response = iam_client.get_user()
        print()
        print(f'{MinStyle.PINK}IAM get-user Response using tmp session credentials{MinStyle.RESET}')
        print(f'{MinStyle.LIGHTGREY}{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
        print(f'{MinStyle.LIGHTCYAN}UserName: {MinStyle.WHITE}{get_user_response.get("User").get("UserName")}{MinStyle.RESET}')
        print(f'{MinStyle.LIGHTCYAN}UserId: {MinStyle.WHITE}{get_user_response.get("User").get("UserId")}{MinStyle.RESET}')
        print(f'{MinStyle.LIGHTCYAN}Arn: {MinStyle.WHITE}{get_user_response.get("User").get("Arn")}{MinStyle.RESET}')
        print()
    except iam_client.exceptions.NoSuchEntityException as err:
        print(f'No Such Entity Exception:\n{err}')
    except iam_client.exceptions.ServiceFailureException as err:
        print(f'Service Failure Exception:\n{err}')
    except botocore.exceptions.ClientError as err:
        errMessage(err, action)
    return

# setting initial variables and assigning input args
mfa_token = args.mfa_token
st_profile = args.base_profile
mfa_tmp_creds_profile = args.tmp_profile
aws_profile_to_mod = args.aws_credentials_file
mfa_arn = args.mfa_arn
dur_seconds = args.duration_seconds

# display the input mfa_token
print(f'\n{MinStyle.PINK}Attempting to obtain temporary Session Credentials using{MinStyle.RESET}')
print(f'{MinStyle.WHITE}{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}AWS Profile: {MinStyle.WHITE}{st_profile}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}MFA Token:   {MinStyle.WHITE}{mfa_token}{MinStyle.RESET}\n')

# get and display the caller identity to validate that the default profile is the correct one
getCallerIdentity(st_profile)


# get and display the temporary credentials obtained using the mfa token
st_session = boto3.Session(profile_name=(st_profile))
st_profile_sts_client = st_session.client('sts')
session_token_response = st_profile_sts_client.get_session_token(
    DurationSeconds=(dur_seconds),
    SerialNumber=(mfa_arn),
    TokenCode=(mfa_token)
)
access_key_id = session_token_response.get("Credentials").get("AccessKeyId")
secret_access_key = session_token_response.get(
    "Credentials").get("SecretAccessKey")
session_token = session_token_response.get("Credentials").get("SessionToken")

# get and display the profile that is about to be modified
config.read(f'{aws_profile_to_mod}')
if args.verbose:
    print(f'{MinStyle.PINK}Temporary Profile Credentials Original Values')
    print(f'{MinStyle.LIGHTGREY}{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
    print(f'{MinStyle.LIGHTCYAN}Profile: {MinStyle.YELLOW}{mfa_tmp_creds_profile}{MinStyle.RESET}')
    print(f'{MinStyle.LIGHTCYAN}AccessKeyId: {MinStyle.YELLOW}{config.get(f"{mfa_tmp_creds_profile}", "aws_access_key_id")}{MinStyle.RESET}')
    print(f'{MinStyle.LIGHTCYAN}SecretAccessKey: {MinStyle.YELLOW}{config.get(f"{mfa_tmp_creds_profile}", "aws_secret_access_key")}{MinStyle.RESET}')
    print(f'{MinStyle.LIGHTCYAN}SessionToken: {MinStyle.YELLOW}{config.get(f"{mfa_tmp_creds_profile}", "aws_session_token")}{MinStyle.RESET}')

# set the new values of the to be modified profile and then write them out
config.set(f'{mfa_tmp_creds_profile}', 'aws_access_key_id', f'{access_key_id}')
config.set(f'{mfa_tmp_creds_profile}', 'aws_secret_access_key', f'{secret_access_key}')
config.set(f'{mfa_tmp_creds_profile}', 'aws_session_token', f'{session_token}')
with open((aws_profile_to_mod), 'w') as configfile:
    config.write(configfile)

# display the new values of the now modified profile
if args.verbose:
    print()
    print(f'{MinStyle.PINK}New Temporary Session Token Credentials')
    print(f'{MinStyle.LIGHTGREY}{MinStyle.DIV_SINGLE_MEDIUM}{MinStyle.RESET}')
    print(f'{MinStyle.LIGHTCYAN}Modified Profile: {MinStyle.YELLOW}{mfa_tmp_creds_profile}{MinStyle.RESET}')
    print(f'{MinStyle.LIGHTCYAN}AccessKeyId: {MinStyle.YELLOW}{access_key_id}{MinStyle.RESET}')
    print(f'{MinStyle.LIGHTCYAN}SecretAccessKey: {MinStyle.YELLOW}{secret_access_key}{MinStyle.RESET}')
    print(f'{MinStyle.LIGHTCYAN}SessionToken: {MinStyle.YELLOW}{session_token}{MinStyle.RESET}')
    print()

# get and display the users identity using the new profile to validate that the temp credentials work
getUser(mfa_tmp_creds_profile)

# Display success message
print(f'{MinStyle.GREEN}Success! {MinStyle.WHITE}Temporary Session Credentials obtained and stored in the {MinStyle.LIGHTCYAN}st_mfa_creds{MinStyle.WHITE} profile{MinStyle.RESET}\n')
