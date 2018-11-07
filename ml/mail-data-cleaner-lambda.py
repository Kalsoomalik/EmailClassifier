import json
import boto3
import os
import csv
import re
from datetime import datetime
from datetime import date
from datetime import time
import dateutil.parser
from io import TextIOWrapper
from gzip import GzipFile


message_flag = False
email_date = ""
email_from = ""
folder_date = ""

def lambda_handler(event, context):

    source_bucket_name = "mail.mlvisualizer.com"
    source_file_name = ""
    target_bucket_name = "maildata.mlvisualizer.com"
    target_key = ""
    lambda_inputpath = "/tmp/input.txt"
    lambda_outputpath = "/tmp/ouput.txt"

    data = event.get('Records')[0]
    data = data.get('ses')
    data = data.get('mail')
    source_file_name = data.get('messageId')

    client = boto3.client('s3')
    obj = client.get_object(Bucket=source_bucket_name, Key=source_file_name)
    output =  obj['Body'].read()

    # write file locally
    result = ""
    with open(lambda_inputpath, 'w') as file:
        result = output.decode("utf-8")
        file.write(result)
        file.close()

    # generate ouput file
    parser(lambda_inputpath,lambda_outputpath)

    # copy processed file to target bucket location
    # Replace <ACCOUNT_NUMBER> with aws account number
    # where target bucket is located
    sts_client = boto3.client('sts')
    assumedRoleObject = sts_client.assume_role(
        RoleArn="arn:aws:iam::<ACCOUNT_NUMBER>:role/s3-multiple-account-role",
        RoleSessionName="AssumeRoleSession1"
    )
    credentials = assumedRoleObject['Credentials']
    s3_ml = boto3.resource('s3',
                           aws_access_key_id = credentials['AccessKeyId'],
                           aws_secret_access_key = credentials['SecretAccessKey'],
                           aws_session_token = credentials['SessionToken'],
                           )
    target_key = folder_date + "/" + email_from[0] + "/" + email_date + ".txt"
    print(target_key)
    object = s3_ml.Object(target_bucket_name, target_key)
    object.put(Body=open(lambda_outputpath,'rb'))

    # submit message to queue
    createSQSNotification(target_bucket_name, target_key)

    return {
        "statusCode": 200,
        "body": json.dumps('Email Processed.'),
    }


def parser(inputpath, ouputpath):
    inputfile = open(inputpath, "r")
    outputfile = open(ouputpath, "w")
    for line in inputfile:
        writeFrom(outputfile, line)
        writeTo(outputfile, line)
        writeSubject(outputfile, line)
        writeDate(outputfile, line)
        flagMessageStart(outputfile, line)
        flagMessageStop(outputfile, line)
        writeMessage(outputfile, line)
        # print(line)
    outputfile.close()
    inputfile.close();

def writeTo(outputfile, line):
    if message_flag == False:
        result = re.findall(r'^To: ', line, flags=re.MULTILINE)
        if result:
            outputfile.write(line)


def writeFrom(outputfile, line):
    global email_from
    if message_flag == False:
        result = re.findall(r'^From: ', line, flags=re.MULTILINE)
        if result:
            outputfile.write(line)
    result = re.findall(r'^From: ', line, flags=re.MULTILINE)
    if result:
        email_from = line[5:].strip()
        # print(email_from)
        email_from = re.findall('(?<=@)[a-z]+[.][a-z]{3}', email_from)
        # print(email_from)


def writeSubject(outputfile, line):
    if message_flag == False:
        result = re.findall(r'^Subject: ', line, flags=re.MULTILINE)
        if result:
            outputfile.write(line)


def writeDate(outputfile, line):
    global email_date
    global folder_date
    if message_flag == False:
        result = re.findall(r'^Date: ', line, flags=re.MULTILINE)
        if result:
            outputfile.write(line)
    result = re.findall(r'^Date: ', line, flags=re.MULTILINE)
    if result:
        email_date = line[5:].strip()
        if email_date:
            emailDate  = dateutil.parser.parse(email_date);
            year =  emailDate.strftime("%Y");
            month =  emailDate.strftime("%m");
            day =  emailDate.strftime("%d");
            hour =  emailDate.strftime("%H");
            minute =  emailDate.strftime("%M");
            email_date = year + month + day + hour + minute
            folder_date = year + "-" + month + "-" + day

def flagMessageStart(outputfile, line):
    result = re.findall("text/plain; charset=", line)
    global message_flag
    if result:
        message_flag = True


def flagMessageStop(outputfile, line):
    result = re.findall("--000000000000", line)
    global message_flag
    if result:
        if message_flag == True:
            message_flag = False


def writeMessage(outputfile, line):
    if message_flag == True:
        result = re.search("text/plain; charset=", line)
        if result is None:
            result = re.search("Content-Transfer-Encoding", line)
            if result is None:
                outputfile.write(line)

def createSQSNotification(bucket, target_key):
    sts_client = boto3.client('sts')

    # Replace <ACCOUNT_NUMBER> with aws account number
    # where target SQS Queue is located
    assumedRoleObject = sts_client.assume_role(
        RoleArn="arn:aws:iam::<ACCOUNT_NUMBER>:role/s3-multiple-account-role",
        RoleSessionName="AssumeRoleSession1"
    )
    credentials = assumedRoleObject['Credentials']
    sqs = boto3.resource('sqs',
                         aws_access_key_id = credentials['AccessKeyId'],
                         aws_secret_access_key = credentials['SecretAccessKey'],
                         aws_session_token = credentials['SessionToken'],
                         )
    queue = sqs.get_queue_by_name(QueueName='mail-data-analyzer')
    queue.send_message(MessageBody='boto3', MessageAttributes={
        'target_key': {
            'StringValue': target_key,
            'DataType': 'String'
        }
    })