### Create stack

- - -

* minimal template file

``` shell
aws cloudformation create-stack --stack-name jhs3stack112 --template-body file://lab111-minimal-s3.yaml
```
<br>
* passing parameters via a file

``` shell
aws cloudformation create-stack --stack-name jhs3stack112 --template-body file://lab112-minimal-s3.yaml --parameters file://s3-params.json
```
<br>
### Delete stack

- - -

``` shell
aws cloudformation delete-stack --stack-name jhs3stack112
```
<br>
### Update a stack

- - -

``` shell
aws cloudformation update-stack --stack-name jhs3stack --template-body file://lab113-s3-pseudo-parameters.yaml --parameters file://s3-params.json
```
<br>
### Key aws cli options

- - -

* To deploy to another region: \`--region <region\_name>\`

``` javascript
aws --region us-east-2 cloudformation create-stack --stack-name jhs3stack --template-body file://lab114-s3-conditions.yaml --parameters file://s3-params.json
```
<br>
* To use a specific profile: \`--profile <profile\_name>\`

``` shell
aws --profile st_jh_labs cloudformation create-stack --stack-name jhs3stack --template-body file://lab114-s3-conditions.yaml --parameters file://s3-params.json
```

* When using an IAM command, you must include the --capabilities CAPABILITY\_NAMED\_IAM, parameter to specificlly tell the CLI to execute it (it's a built-in safegard)

``` shell
aws cloudformation create-stack --stack-name jh4stack --template-body file://lab121-cross-reference.yaml --parameters file://params.json --capabilities CAPABILITY_NAMED_IAM
```
<br>
#### Commandline Command

- - -

<br>
<br>
aws cloudformation create-stack --stack-name jh4stack --template-body file://lab121-cross-reference.yaml --parameters file://params.json --capabilities CAPABILITY\_NAMED\_IAM