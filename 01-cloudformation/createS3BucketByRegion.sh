#!/usr/bin/env bash

# ===========================================================================================================
# Author: John Hunter    Initial creation: 22Jun2021
# 
# Description:
#     Given a country, an s3 bucket will be created in each of its regions
# 
# Arguments:
#     o inputCountry - the desired country to have s3 buckets created in
#
# Requirements:
#     o file: <cloudformation_file> - the file that contains the s3 stack and used to create the buckets
#     o file: <regions_config> - A yaml configuration file that contains the countries and their regions
# 
# Further Enhancements:
#     o Instead of requesting the country as input, make everything a paramater
#     o Implement paramenters for the script. If the command is called with no arguments, display usage instructions
#       -h, --h : to get help output like a standard bash command
#       -c, --country : the desired country to create the s3 buckets in
#       --stack-name : the base, custom user name that will have the current-region appended to it
#       --region-config : the region config file containing the countries and their regions
#       --template-body : the file  containing the stack s3 bucket creation template
#     o Read the countries into an array from the regions_config yaml file and use that for the country
#       validation check instead of having it hard coded
# 
# Notes:
#     - I had to hard code the path to 'yq' since there is this one, for bash and I have another installed
#       for python. What a pain.
# 
# ===========================================================================================================

# setting some color varibles for use
#  --------------------------------------
BLACK=$(tput setaf 0)
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
DARK_BLUE=$(tput setaf 4)
MAGENTA=$(tput setaf 5)
SKY_BLUE=$(tput setaf 6)
WHITE=$(tput setaf 7)
GREY=$(tput setaf 8)
BRICK_RED=$(tput setaf 9)
BRIGHT_GREEN=$(tput setaf 10)
BRIGHT_YELLOW=$(tput setaf 11)
BLUE=$(tput setaf 12)
PURPLE=$(tput setaf 13)
CYAN=$(tput setaf 14)
BRIGHT_WHITE=$(tput setaf 15)
DIRTY_WHITE=$(tput setaf 250)

doubleDiv===========================================================================================================
singleLongDiv=------------------------------------------------------------------------------------------------
singleDiv=----------------------------

# ============= setting all variables ===============
countries=("usa" "eu")
configFile="regions-config.yaml"
logFile="$(basename "$0" .sh).output.$(date '+%Y-%m-%d_%H.%M.%S').txt"

# checking if required command-line tools exist: yq
yq --version &> /dev/null
if [[ $? != 0 ]] ; then
    printf "\n%s\n\n" "${BRIGHT_WHITE}$doubleDiv${BRIGHT_WHITE}"
    printf "%s\n\n" "${RED} Error. ${DIRTY_WHITE}Required command-line tool ${YELLOW}yq${DIRTY_WHITE} not found. Please install before continuing. ${RED}Exiting${DIRTY_WHITE}"
    printf "%s\n\n" "${BRIGHT_WHITE}$doubleDiv${BRIGHT_WHITE}"
    exit 1
fi

# starting script and requesting a country to create the s3 buckets in
printf "\n%s" "${GREEN}Step 1. ${BRIGHT_WHITE}Please input a country to create S3 buckets in each region ${CYAN}(usa, eu) ${PURPLE}"
read inputCountry
printf "${BRIGHT_WHITE}\n"

# Validating the country value and exiting if not valid
inputErrMsg="  ${RED}ERROR. ${BRIGHT_WHITE}Incorrect country input."
inputErrMsg2="  ${BRIGHT_WHITE}Input one of --> ${CYAN}[ usa, eu ]${DIRTY_WHITE}"
if [[ $inputCountry != "usa" && $inputCountry != "eu" ]] ; then
    printf "\n%s\n\n" "${WHITE}${doubleDiv}"
    printf "%s\n\n%s\n\n" "$inputErrMsg" "$inputErrMsg2"
    printf "%s\n\n" "${WHITE}${doubleDiv}"
    exit 1
fi

# getting the regions for the input country selected and formatting,trimming before stuffing the regions
# in an array
rawRegions=$(yq eval "with_entries(select(.key | . == \"$inputCountry\")) | .[][]" $configFile | tr -s '\n' ',' )
trimmedRegions=${rawRegions::-1}
IFS=',' read -r -a regionsArray <<< ${trimmedRegions}
arrayLen=${#regionsArray[@]}

# displaying pre-execution info
printf "%s\n\n" "        ${BRIGHT_WHITE}Input country \"${PURPLE}$inputCountry${BRIGHT_WHITE}\" has ${CYAN}$arrayLen${BRIGHT_WHITE} regions where an S3 bucket will be created.${BRIGHT_WHITE}"
printf "\n%s\n\n" "${GREEN}Step 2. ${BRIGHT_WHITE}Creating S3 bucket in each region"

exit 1

# looping through the regions and creating an s3 bucket in each
for region in "${regionsArray[@]}"
do
    stackName="jhS3stack-"$region
    printf "%s" "        ${BRIGHT_WHITE}Attempting to create S3 bucket in region: ${CYAN}$region${BRIGHT_WHITE} ..."
    # creating the stack
    rawStackId=$(aws --region $region cloudformation create-stack --stack-name $stackName --template-body file://lab131-s3.yaml --capabilities CAPABILITY_NAMED_IAM | tee "$logFile")
    stackId=$(echo $rawStackId | tr -d '{}\n"' | cut -d ' ' -f3)
    # validating that the stack was created successfuly and can be used
    aws --region $region cloudformation wait stack-create-complete --stack-name $stackId
    if [[ $?==0 ]]; then
        # success messages
        printf "%s\n" "  ${GREEN}Success!  ${BRIGHT_WHITE}S3 bucket created.${BRIGHT_WHITE}"
        printf "%s\n\n" "        ${YELLOW}StackId: ${BRIGHT_WHITE}$stackId${BRIGHT_WHITE}"
    else
        # error messages
        printf "\n\n%s\n\n" "${BRIGHT_WHITE}$doubleDiv${BRIGHT_WHITE}"
        printf "%s\n\n" "  ${RED}ERROR  ${BRIGHT_WHITE}Stack ${BRIGHT_YELLOW}$stackName${BRIGHT_WHITE} failed creation in region ${CYAN}$region${BRIGHT_WHITE}. S3 bucket not created. ${RED}Exiting.${BRIGHT_WHITE}"
        printf "%s\n\n" "  ${DIRTY_WHITE}For more details, view the logfile: $logFile${BRIGHT_WHITE}"
        printf "%s\n\n" "${BRIGHT_WHITE}$doubleDiv${BRIGHT_WHITE}"
        exit 1
    fi
done

# if the script is successful, remove logfiles
rm $logFile

# displaying overall success and run time message
printf "\n%s\n\n" "${WHITE}${doubleDiv}"
min=0
sec=$SECONDS
if [ "$SECONDS" -gt "60" ] ; then
    min=$((SECONDS / 60))
    sec=$((SECONDS % 60))
fi
printf "%s\n\n" "${BRIGHT_WHITE}Script run time: ${YELLOW}$min${DIRTY_WHITE} minutes, ${YELLOW}$sec${DIRTY_WHITE} seconds"
printf "%s\n" "${BRIGHT_GREEN}SUCCESS ${CYAN}$(basename $0)${BRIGHT_WHITE} completed successfully"
printf "\n%s\n\n" "${WHITE}${doubleDiv}"
