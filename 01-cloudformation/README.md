# Topic 1: CloudFormation

* [Topic 1: CloudFormation](#topic-1-cloudformation)
    * [Conventions](#conventions)
    * [Lesson 1.1: Introduction to CloudFormation](#lesson-11-introduction-to-cloudformation)
        * [Principle 1.1](#principle-11)
        * [Practice 1.1](#practice-11)
            * [Lab 1.1.1: CloudFormation Template Requirements](#lab-111-cloudformation-template-requirements)
            * [Lab 1.1.2: Stack Parameters](#lab-112-stack-parameters)
            * [Lab 1.1.3: Pseudo-Parameters](#lab-113-pseudo-parameters)
            * [Lab 1.1.4: Using Conditions](#lab-114-using-conditions)
            * [Lab 1.1.5: Termination Protection; Clean up](#lab-115-termination-protection-clean-up)
        * [Retrospective 1.1](#retrospective-11)
            * [Question: Why YAML](#question-why-yaml)
            * [Question: Protecting Resources](#question-protecting-resources)
            * [Task: String Substitution](#task-string-substitution)
    * [Lesson 1.2: Integration with Other AWS Resources](#lesson-12-integration-with-other-aws-resources)
        * [Principle 1.2](#principle-12)
        * [Practice 1.2](#practice-12)
            * [Lab 1.2.1: Cross-Referencing Resources within a Template](#lab-121-cross-referencing-resources-within-a-template)
            * [Lab 1.2.2: Exposing Resource Details via Exports](#lab-122-exposing-resource-details-via-exports)
            * [Lab 1.2.3: Importing another Stack's Exports](#lab-123-importing-another-stacks-exports)
            * [Lab 1.2.4: Import/Export Dependencies](#lab-124-importexport-dependencies)
        * [Retrospective 1.2](#retrospective-12)
            * [Task: Policy Tester](#task-policy-tester)
            * [Task: SSM Parameter Store](#task-ssm-parameter-store)
    * [Lesson 1.3: Portability & Staying DRY](#lesson-13-portability--staying-dry)
        * [Principle 1.3](#principle-13)
        * [Practice 1.3](#practice-13)
            * [Lab 1.3.1: Scripts and Configuration](#lab-131-scripts-and-configuration)
            * [Lab 1.3.2: Coding with AWS SDKs](#lab-132-coding-with-aws-sdks)
            * [Lab 1.3.3: Enhancing the Code](#lab-133-enhancing-the-code)
        * [Retrospective 1.3](#retrospective-13)
            * [Question: Portability](#question-portability)
            * [Task: DRYer Code](#task-dryer-code)
    * [Additional Reading](#additional-reading)

## Conventions

* All CloudFormation templates should be
[written in YAML](https://getopentest.org/reference/yaml-primer.html)
* Do NOT copy and paste CloudFormation templates from the Internet at large
* DO use the [CloudFormation documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-reference.html)
* DO utilize every link in this document; note how the AWS documentation is
laid out
* DO use the [AWS CLI for CloudFormation](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/index.html#)
(NOT the Console) unless otherwise specified.

## Lesson 1.1: Introduction to CloudFormation

### Principle 1.1

AWS CloudFormation (CFN) is the preferred way we create AWS resources at Stelligent

### Practice 1.1

A CFN Template is essentially a set of instructions for creating AWS
resources, which includes practically everything that can be created in
AWS. At its simplest, the service accepts a Template (a YAML-based
blueprint describing the resources you want to create or update) and
creates a Stack (a set of resources created using a single template).
The resulting Stacks represent groups of resources whose life-cycles are
inherently linked.

Read through [Template Anatomy](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-anatomy.html)
and get familiar with the basic parts of a CloudFormation template.

#### Lab 1.1.1: CloudFormation Template Requirements

Create the *most minimal CFN template possible* that can be used to
create an AWS Simple Storage Service (S3) Bucket.

* Always write your CloudFormation [templates in YAML](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-formats.html).
* Launch a Stack by [using the AWS CLI tool](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/create-stack.html)
to run the template. Use your preferred region.
* Note the output provided by creating the Stack.
* Though *functionally* unnecessary, the Description (i.e. its *purpose*)
element documents your code's *intent*, so provide one. The Description
key-value pair should be at the *root level* of your template. If you place
it under the definition of a resource, AWS will allow the template's creation
but your description will not populate anything. See
[here](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-anatomy.html)
for a useful guide to the anatomy of a template as well as
[YAML terminology](https://yaml.org/spec/1.2/spec.html#id2759768).
* Commit the template to your Github repository under the 01-cloudformation
folder.

#### Lab 1.1.2: Stack Parameters

Update the same template by adding a CloudFormation
[Parameter](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html)
to the stack and use the parameter's value as the name of the S3 bucket.

* Put your parameter into a separate JSON file and pass that file to the CLI.
* Update your stack.
* Add the template changes and new parameter file to your Github repo.

#### Lab 1.1.3: Pseudo-Parameters

Update the same template by prefixing the name of the bucket with the
Account ID in which it is being created, no matter which account you're
running the template from (i.e., using
[pseudo-parameters](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/pseudo-parameter-reference.html)).

* Use built-in CFN string functions to combine the two strings for the Bucket name.
* Do not hard code the Account ID. Do not use an additional parameter to
provide the Account ID value.
* Update the stack.
* Commit the changes to your Github repo.

#### Lab 1.1.4: Using Conditions

Update the same template one final time. This time, use a CloudFormation
[Condition](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html)
to add a prefix to the name of the bucket. When the current execution
region is your preferred region, prefix the bucket name with the
Account ID. When executing in all other regions, use the region
name.

* Update the stack that you originally deployed.
* Create a new stack *with the same stack name*, but this time
deploying to some region other than your preferred region.
* Commit the changes to your Github repo.

#### Lab 1.1.5: Termination Protection; Clean up

* Before deleting this lesson's Stacks, apply
[Termination Protection](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-protect-stacks.html)
to one of them.
* Try to delete the Stack using the AWS CLI. What happens?
* Remove termination protection and try again.
* List the S3 buckets in both regions once this lesson's Stacks have been
deleted to ensure their removal.

### Retrospective 1.1

#### Question: Why YAML

*Why do we prefer the YAML format for CFN templates?*

> It is cleaner and easier to read for a human.  JSON comes with all of the extra
> baggage needed to describe an object using quotes, curly braces, etc.

#### Question: Protecting Resources

*What else can you do to prevent resources in a stack from being deleted?*
<br>
> There are four approaches to prevent a stack from being deleted.
> 
> 
> 1. You can set the DeletionPolicy attributed on ALL of the resources within the stack.
> 2. You can modify the IAM permissions so that the the user does not have the ability to delete a stack.
> 3. The stack has an overall policy that can be set to prevent deletion
> 4. Enable termination protection so that a person cannot delete a stack

See [DeletionPolicy](https://aws.amazon.com/premiumsupport/knowledge-center/cloudformation-accidental-updates/).

*How is that different from applying Termination Protection?*

> Termination Protection is a stack level setting that applies to the entire
> stack whereas the *DeletionPolicy* attribute only applies to each resource. If
> you wanted to have the same behavior as *Termination Protection*, you would have
> to set the attribute for every single resource in the stack.

#### Task: String Substitution

Demonstrate 2 ways to code string combination/substitution using
built-in CFN functions.

> 1. Using a Condition, you can test using the supported conditions (And, Equals, If, Not, Or) and, depending on the result, use the IF function with JOIN to combine or with simply the string by itself
> 2. Using a Condition, use the Substitute function SUB to select a value to combine or substitute.

## Lesson 1.2: Integration with Other AWS Resources

### Principle 1.2

CloudFormation integrates well with the rest of the AWS ecosystem

### Practice 1.2

A CFN template's resources can reference: each other's attributes,
resource attributes exported from other Stacks in the same region, and
Systems Manager Parameter Store values in the same region. This provides
a way to have resources build on each other to create your AWS
ecosystem.

#### Lab 1.2.1: Cross-Referencing Resources within a Template

Create a CFN template that describes two resources: an IAM User, and an
IAM Managed Policy that controls that user.

* The policy should allow access solely to 'Read' actions against all
S3 Buckets (including listing buckets and downloading individual bucket contents)
* Attach the policy to the user via the template.
* Use a CFN Parameter to set the user's name
* Create the Stack.

> This was a bit confusing to me at first since I didn't realize that there were specific
> AWS Types for different policies. At first, I was using 'AWS::IAM::Policy' which creates
> inline policies which is not what I wanted (especially since they don't have their own
> ARNs). After some doing some googling and reading further in the AWS docs, I realized that
> I needed to use 'AWS::IAM::ManagedPolicy' instead to create the right type of policy. Once
> I did that, things worked as expected. The cli that I used:

<br>
```
aws cloudformation create-stack --stack-name jh4stack --template-body file://lab121c-cross-reference-managed.yaml --parameters file://params.json --capabilities CAPABILITY_NAMED_IAM
```

#### Lab 1.2.2: Exposing Resource Details via Exports

Update the template by adding a CFN Output that exports the Managed
Policy's Amazon Resource Name ([ARN](https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html)).

* Update the Stack.
* [List all the Stack Exports](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/list-exports.html)
in that Stack's region.

> Again, this took longer than expected since the cloudformation syntax is still new to me and
> a little strange from what I am used to - but it is getting clearer and I'm getting faster.
> It took me a bit to get the exports working since I inadvertently thought that the '*Export*'
> notation took two parts, a name and a value and then I realized that the presence of the
> '*Export*' label was what triggered aws to export the output value and that the '*Export*' name
> was simply the name of the output value when exported. Seems simple now but it was really
> confusing at first. The cli that I used:

<br>
```
aws cloudformation create-stack --stack-name jh5stack --template-body file://lab122-exposing-exports.yaml --parameters file://params.json --capabilities CAPABILITY_NAMED_IAM
```
<br>
#### Lab 1.2.3: Importing another Stack's Exports

Create a *new* CFN template that describes an IAM User and applies to it
the Managed Policy ARN created by and exported from the previous Stack.

* Create this new Stack.
* [List all the Stack Imports](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/list-imports.html)
in that stack's region.

> I read this *too fast* and *assumed* that it meant to create the new user
> in another region. But, as I learned, you can't import exported values
> cross-region, only in the same region. So I guess this was a good learning
> point for me. Once I realized my mistake, this went fast.
> The cli that I used:

<br>
```
aws cloudformation create-stack --stack-name jh6stack --template-body file://lab123-using-imports.yaml --parameters file://params-2.json --capabilities CAPABILITY_NAMED_IAM
```

#### Lab 1.2.4: Import/Export Dependencies

Delete your CFN stacks in the same order you created them in. Did you
succeed? If not, describe how you would *identify* the problem, and
resolve it yourself.
<br>
> Deleting stacks in the same order that you created them will not work if
> later created stacks reference earlier created stacks.  They will not
> successfully delete since there are dependencies on their resources. In order
> to successfully delete them, you must do the deletion in reverse order, starting
> with the most recently created and then deleting in reverse chronological order.
> 
> When doing anything with the aws cli, it is always best to use commands to verify
> that your command successfully executed. In this case, I would use the
> 'aws cloudformation describe-events --stack-name \<stack>' with the expectation
> that it would come back with an error stating that the stack does not exist. If it
> comes back with anything else, it will list in the events what the issue was that
> prevented the deletion command from succeeding, specifically that the stack could
> not be deleted because of dependency issues. Knowing the issue that prevented the
> command from succeeding enables you to fix the issue so that it can succeed.

### Retrospective 1.2

#### Task: Policy Tester

Show how to use the IAM policy tester to demonstrate that the user
cannot perform 'Put' actions on any S3 buckets.
<br>
> Using the aws IAM Policy Tester is very simple. You simply select the
> policy that you want to test, select the resources and then select the
> actions that you want to run against it.  You will the action results
> and they should be exactly what you expect.  If any of the action results
> are not what you expect, such as the IAM user can read or can delete, or
> whatever, and the policy should not allow it, then you modify the policy
> and then follow the process again until the policy does exactly as you
> are expecting.

#### Task: SSM Parameter Store

Using the AWS Console, create a Systems Manager Parameter Store
parameter in the same region as the first Stack, and provide a value for
that parameter. Modify the first Stack's template so that it utilizes
this Parameter Store parameter value as the IAM User's name. Update the
first stack. Finally, tear it down.
<br>
> This one was pretty straight forward and worked right off. :)
> The cli that I used:

<br>
```
aws cloudformation create-stack --stack-name jhstack-7 --template-body file://lab124-using-ssm.yaml --parameters file://params-ssm.json --capabilities CAPABILITY_NAMED_IAM
```

## Lesson 1.3: Portability & Staying DRY

### Principle 1.3

*CloudFormation templates should be portable, supporting*
[Don't Repeat Yourself](http://wiki.c2.com/?DontRepeatYourself) (DRY)
practices.

### Practice 1.3

Portability refers to the ability of code (whether it's a script or an
entire application) to work in multiple execution environments. This is
achieved most often by removing hard coded configuration elements and
providing an environment-specific configuration file. For CFN templates,
portability is best provided by parameterizing the template (refer to
[AWS CloudFormation Best Practices](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#reuse)
for a more thorough list of recommendations for improving your use of
CloudFormation). Some lab exercises have already demonstrated
portability (*can you point out where?*) and this lesson will focus
on it specifically.

#### Lab 1.3.1: Scripts and Configuration

Create a single script that re-uses one CloudFormation template to
deploy *a single S3 bucket*.

* Use shell scripting (bash or PowerShell) to create a Stack in each
of the [4 American regions](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html),
using a looping construct to run the template the proper number of times.
* Use an external JSON or YAML configuration file to maintain the target
deployment region parameters. Consider using `jq` or `yq` to parse this file.
* Each bucket name should be of the format
"*current-Region*-*current-Account*-*friendly-name*"
where the "*friendly-name*" value is parameterized in the CFN template
but has a default value.

> Wrote a bash script: createS3BucketByRegion.sh

#### Lab 1.3.2: Coding with AWS SDKs

Repeat the exercise in the previous lab, with two modifications:

* Use only a programming language
([Python](https://aws.amazon.com/developers/getting-started/python/),
[Ruby](https://aws.amazon.com/developers/getting-started/ruby/)
or [Javascript - i.e. NodeJS](https://aws.amazon.com/developers/getting-started/nodejs/))
and the corresponding SDK to repeat exactly what was done in that lab.
* Extend the region targets (i.e. modify your configuration file) to
include another US region.

Also adhere to these criteria:

* The code must support updating existing stacks and creating new
ones. This can be tricky as some SDKs require that you use a
'try/catch' construct to determine the existence of a stack.
(Using rescue-oriented structures for decision logic is generally
considered a programming anti-pattern.)
* Use only a single shell command to execute your code script.

#### Lab 1.3.3: Enhancing the Code

Add code that provides for the deletion of your CFN stacks using the
same configuration list, and then delete the stacks using that new
functionality. Query S3 to ensure that the buckets have been deleted.

* Commit your changes to your latest branch.

> Python script: manageS3Buckets.py
> 
> Completed all of the functionality required by lab 1.3.1 to 1.3.3 in
> a the python file.

### Retrospective 1.3

#### Question: Portability

*Can you list 4 features of CloudFormation that help make a CFN template*
portable code?

#### Task: DRYer Code

How reusable is your SDK-orchestration code? Did you share a single
method to load the configuration file for both stack creation/updating
(Lab 1.3.2) and deletion (Lab 1.3.3)? Did you separate the methods for
finding existing stacks from the methods that create or update those stacks?

If not, refactor your Python, Ruby or NodeJS scripts to work in the
manner described.
<br>
> I created functions that can be reused by other scripts. There are
> separate functions to create/update a cloudformation stack, delete
> a stack and separate error functions.  They can all be reused.

## Additional Reading

Related topics to extend your knowledge about CloudFormation:

* Using [Stack Policies](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/protect-stack-resources.html)
to apply permissions to modify a stack
* Using [StackSets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/what-is-cfnstacksets.html)
to deploy a CloudFormation stack simultaneously across an array of
AWS Account and Regions