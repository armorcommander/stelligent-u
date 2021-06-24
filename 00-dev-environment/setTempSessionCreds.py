#!/usr/bin/env python3

# ===========================================================================================================
# Author: John Hunter    Initial creation: 14Jun2021
#
# Description:
#     This takes an input MFA token and gets a temporary session token that is used to create
#     temporary credentials for programatically accessing AWS for a limited duration
#
# Arguments:
#     A valid MFA token
#
# ===========================================================================================================
#
# Additional TODO
#  - Validation of the MFA token
#  - Add '-q, --quiet' option that would silence the verbose output


import argparse
import configparser
import os
import sys

import boto3

# appending the path so that packages can be imported from a parent level
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from utils.pyColors import MinStyle  # isort:skip


# create the commandline parser
my_parser = argparse.ArgumentParser(prog='setTempSessionCreds',
                                    usage='%(prog)s [-h] mfa_token',
                                    description='Use your MFA Token to create temporary credentials using a session token')

# adding cli arguments
my_parser.add_argument('MFA_Token',
                       metavar='mfa_token',
                       type=str,
                       help='The MFA token used to obtain the temporary session token')

# execute the parse_args() method
args = my_parser.parse_args()

# assigning the input token
mfa_token = args.MFA_Token

config = configparser.ConfigParser()

# setting initial variables
st_profile = 'st_jh_labs'
mfa_creds_profile = 'st_mfa_creds'
mfa_token = sys.argv[1]
MODFILE = '/Users/John.Hunter/.aws/credentials'
mfa_arn = 'arn:aws:iam::324320755747:mfa/john.hunter.labs'

# display the input mfa_token
print(f'\nMFA Token: {mfa_token}\n')

# get and display the caller idenity to validate that the default profile is the correct one
st_session = boto3.Session(profile_name=(st_profile))
st_profile_sts_client = st_session.client('sts')
caller_identity_response = st_profile_sts_client.get_caller_identity()

print(f'{MinStyle.PINK}STS Caller Identity values{MinStyle.RESET}')
print(f'{MinStyle.LIGHTGREY}{MinStyle.DIV_SINGLE_SHORT}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}UserId: {MinStyle.WHITE}{caller_identity_response.get("UserId")}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}Account: {MinStyle.WHITE}{caller_identity_response.get("Account")}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}Arn: {MinStyle.WHITE}{caller_identity_response.get("Arn")}{MinStyle.RESET}')
print()


# get and display the temporary credentials obtained using the mfa token
dur_seconds = 43200  # 12 hour duration
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
config.read(f'{MODFILE}')
print(f'{MinStyle.PINK}Temporary Profile Credentials Original Values')
print(f'{MinStyle.LIGHTGREY}{MinStyle.DIV_SINGLE_SHORT}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}Profile: {MinStyle.YELLOW}{mfa_creds_profile}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}AccessKeyId: {MinStyle.YELLOW}{config.get(f"{mfa_creds_profile}", "aws_access_key_id")}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}SecretAccessKey: {MinStyle.YELLOW}{config.get(f"{mfa_creds_profile}", "aws_secret_access_key")}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}SessionToken: {MinStyle.YELLOW}{config.get(f"{mfa_creds_profile}", "aws_session_token")}{MinStyle.RESET}')

# set the new values of the to be modified profile and then write them out
config.set(f'{mfa_creds_profile}', 'aws_access_key_id', f'{access_key_id}')
config.set(f'{mfa_creds_profile}',
           'aws_secret_access_key', f'{secret_access_key}')
config.set(f'{mfa_creds_profile}', 'aws_session_token', f'{session_token}')
with open((MODFILE), 'w') as configfile:
    config.write(configfile)

# display the new values of the now modified profile
print()
print(f'{MinStyle.PINK}New Temporary Session Token Credentials')
print(f'{MinStyle.LIGHTGREY}{MinStyle.DIV_SINGLE_SHORT}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}Modified Profile: {MinStyle.YELLOW}{mfa_creds_profile}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}AccessKeyId: {MinStyle.YELLOW}{access_key_id}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}SecretAccessKey: {MinStyle.YELLOW}{secret_access_key}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}SessionToken: {MinStyle.YELLOW}{session_token}{MinStyle.RESET}')
print()


# print(f'{MinStyle.LIGHTCYAN}AWS_PROFILE= {MinStyle.YELLOW}{os.getenv("AWS_PROFILE")}{MinStyle.RESET}\n')
# os.environ['AWS_PROFLE']='st_mfa_creds'
# print(f'{MinStyle.LIGHTCYAN}AWS_PROFILE= {MinStyle.YELLOW}{os.getenv("AWS_PROFILE")}{MinStyle.RESET}\n')

# get and display the users identity using the new profile to validate that the temp credentials work
iam_session = boto3.Session(profile_name=(mfa_creds_profile))
iam_client = iam_session.client('iam')
get_user_response = iam_client.get_user()

print(f'{MinStyle.PINK}IAM get-user Response using tmp session credentials{MinStyle.RESET}')
print(f'{MinStyle.LIGHTGREY}{MinStyle.DIV_SINGLE_SHORT}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}UserName: {MinStyle.WHITE}{get_user_response.get("User").get("UserName")}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}UserId: {MinStyle.WHITE}{get_user_response.get("User").get("UserId")}{MinStyle.RESET}')
print(f'{MinStyle.LIGHTCYAN}Arn: {MinStyle.WHITE}{get_user_response.get("User").get("Arn")}{MinStyle.RESET}')
print()
