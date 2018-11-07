# analyzer.py

import json
import os
import re
from datetime import datetime
from datetime import date
import boto3
import dateutil.parser
import nltk
import numpy as np
import time

nltk.download('punkt')
nltk.download('wordnet')
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer

token_pattern = re.compile(r"(?u)\b\w\w+\b")

class LemmaTokenizer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()

    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc) if len(t) >= 2 and re.match("[a-z].*", t)
                and re.match(token_pattern, t)]

inputpath = os.path.join("/home/ec2-user/scripts/temp", "email.txt")
outputpath = os.path.join("/home/ec2-user/scripts/temp", "output.txt")
jsonpath = os.path.join("/home/ec2-user/scripts/temp", "mail-data-for-visualization.json")
message_flag = False

email_date = ""
email_from = ""
email_text = ""
jsonEmailDate = ""
jsonEmailYear = ""
jsonEmailMonth = ""
jsonEmailDay = ""
jsonEmailTo = ""
jsonEmailFrom = ""
jsonEmailSubject = ""
jsonKeywords = []
jsonCounts = []
jsonOrganizations = []
jsonPersons = []
jsonLocations = []
jsonSentiment = ""
completed = False

client = boto3.client('comprehend')

# Function to process email text
def process(inputpath, ouputpath):
    global completed
    inputfile = open(inputpath, "r")
    outputfile = open(ouputpath, "w")

    # Extract email properties and text
    for line in inputfile:
        writeFrom(outputfile, line)
        writeTo(outputfile, line)
        writeSubject(outputfile, line)
        writeDate(outputfile, line)
        writeMessage(outputfile, line)
        # print(line)
    outputfile.close()
    inputfile.close()

    # Machine learning using AWS Comprehend
    analyzeText(email_text)

    # Machine learning using sklearn and nltk
    analyzeKeywords(None, email_text)

    # Convert information into json format
    writeToJSON()
    completed = True


# Function to extract emailTo property
def writeTo(outputfile, line):
    global jsonEmailTo
    global message_flag
    if message_flag == False:
        result = re.findall(r'^To: ', line, flags=re.MULTILINE)
        if result:
            outputfile.write(line)
            jsonEmailTo = line[3:].strip()
            message_flag = True

# Function to extract emailFrom property
def writeFrom(outputfile, line):
    global email_from
    global jsonEmailFrom
    if message_flag == False:
        result = re.findall(r'^From: ', line, flags=re.MULTILINE)
        if result:
            outputfile.write(line)
    result = re.findall(r'^From: ', line, flags=re.MULTILINE)
    if result:
        email_from = line[5:].strip()
        jsonEmailFrom = email_from
        email_from = re.findall('(?<=@)[a-z]+[.][a-z]{3}', email_from)


# Function to extract emailSubject property
def writeSubject(outputfile, line):
    global jsonEmailSubject
    if message_flag == False:
        result = re.findall(r'^Subject: ', line, flags=re.MULTILINE)
        if result:
            outputfile.write(line)
            jsonEmailSubject = line[8:].strip()

# Function to extract emailDate property
def writeDate(outputfile, line):
    global email_date
    global jsonEmailDate
    global jsonEmailYear
    global jsonEmailMonth
    global jsonEmailDay
    if message_flag == False:
        result = re.findall(r'^Date: ', line, flags=re.MULTILINE)
        if result:
            outputfile.write(line)
    result = re.findall(r'^Date: ', line, flags=re.MULTILINE)
    if result:
        email_date = line[5:].strip()
        if email_date:
            jsonEmailDate = email_date
            emailDate = dateutil.parser.parse(email_date);
            year = emailDate.strftime("%Y");
            month = emailDate.strftime("%m");
            day = emailDate.strftime("%d");
            hour = emailDate.strftime("%H");
            minute = emailDate.strftime("%M");
            email_date = year + month + day + hour + minute
            jsonEmailYear = str(year)
            jsonEmailMonth = str(month)
            jsonEmailDay = str(day)

# Function to extract email text
# Text limit is 4900 characters
def writeMessage(outputfile, line):
    global email_text
    if message_flag == True:
        result = re.search("text/plain; charset=", line)
        if result is None:
            result = re.search("Content-Transfer-Encoding", line)
            if result is None:
                outputfile.write(line)
                if len(email_text) < 4900:
                    email_text = email_text + line


# This function uses AWS Comprehend APIs
# to extract information from email text
def analyzeText(text):
    global jsonLocations
    global jsonPersons
    global jsonOrganizations
    global jsonSentiment
    if len(text) > 1:
        response = client.detect_entities(
            Text=text,
            LanguageCode='en'
        )
        i = 0
        entities = response['Entities']
        while i < len(entities):
            if entities[i]['Type'] == 'LOCATION':
                jsonLocations.append({
                    "name": entities[i]['Text'].replace('\n', ','),
                    "score": str(entities[i]['Score'])
                })
            if entities[i]['Type'] == 'PERSON':
                jsonPersons.append({
                    "name": entities[i]['Text'],
                    "score": str(entities[i]['Score'])
                })
            if entities[i]['Type'] == 'ORGANIZATION':
                result = re.search('[=\@\*<>&\:]+', entities[i]['Text'])
                if result is None:
                    jsonOrganizations.append({
                        "name": entities[i]['Text'],
                        "score": str(entities[i]['Score'])
                    })
            i = i + 1
        # Detect sentiment
        response = client.detect_sentiment(
            Text=text,
            LanguageCode='en'
        )
        jsonSentiment = response['Sentiment']

# This function extract keywords from email text
# using sklearn and nlkt APIs
def analyzeKeywords(ouput, text):
    global jsonKeywords
    if len(text) > 1:
        data = []
        data.append(text)
        vocab_size = 20
        print('Tokenizing and counting, this may take a few minutes...')
        start_time = time.time()
        vectorizer = CountVectorizer(input='content', analyzer='word', stop_words='english',
                                     tokenizer=LemmaTokenizer(), max_features=vocab_size, max_df=1, min_df=1)
        vectors = vectorizer.fit_transform(data)
        vocab_list = vectorizer.get_feature_names()
        idx = np.arange(vectors.shape[0])
        vectors = vectors[idx]

        print('Done. Time elapsed: {:.2f}s'.format(time.time() - start_time))
        vocab_list_count = vectors.toarray()[0]
        keywords = []
        counts = []
        i = 0
        while i < len(vocab_list):
            vocab = vocab_list[i]
            result = re.search('[=_\-\*<>&\:]+', vocab)
            if result is None:
                if len(vocab) < 16:
                    keywords.append(vocab)
                    counts.append(vocab_list_count[i])
            i = i + 1

        if len(keywords) > 5:
            counts_sorted = counts;
            counts_sorted.sort(reverse=True);
            min_count = counts_sorted[4]
            i = 0
            while i < len(counts):
                if counts[i] < min_count:
                    del counts[i]
                    del keywords[i]
                    i = 0
                i = i + 1

        # add to json
        idx = 0
        while idx < len(keywords) and idx < 5:
            jsonKeywords.append(
                {
                    'name': str(keywords[idx]),
                    'count': str(counts[idx])
                }
            )
            idx = idx + 1

# This function converts extracted
# information into json format
def writeToJSON():
    data = {}
    data['dataList'] = []
    dataList = []
    try:
        with open(jsonpath, 'r') as json_file:
            if json_file:
                data = json.load(json_file)
                dataList = data['dataList']
            json_file.close()
    except Exception as e:
        data = {}
        print("File Exception: %s" % e)

    dataList.insert(0, {
        'emailDate': jsonEmailDate,
        'emailYear': jsonEmailYear,
        'emailMonth': jsonEmailMonth,
        'emailDay': jsonEmailDay,
        'emailTo': jsonEmailTo,
        'emailFrom': jsonEmailFrom,
        'emailSubject': jsonEmailSubject,
        'sentiment': jsonSentiment,
        'organizations': jsonOrganizations,
        'locations': jsonLocations,
        'persons': jsonPersons,
        'keywords': jsonKeywords
    })

    # keep list to limited size
    data['dataList'] = dataList[:100]

    with open(jsonpath, 'w') as outfile:
        json.dump(data, outfile)
        outfile.close()

# Function to check and process AWS simple queue service message
def SQSRetrieveMessage():
    # Get the service resource
    sqs = boto3.resource('sqs')
    s3 = boto3.resource('s3')

    # Get the queue
    queue = sqs.get_queue_by_name(QueueName='mail-data-analyzer')

    # Process messages by printing out body and optional author name
    for message in queue.receive_messages(MessageAttributeNames=['target_key']):
        target_key = ''
        if message.message_attributes is not None:
            target_key = message.message_attributes.get('target_key').get('StringValue')

        s3.meta.client.download_file('maildata.mlvisualizer.com',
                                     target_key, '/home/ec2-user/scripts/temp/email.txt')
        try:
            s3.meta.client.download_file('quicksight.mlvisualizer.com', 'data/mail-data-for-visualization.json',
                                         '/home/ec2-user/scripts/temp/mail-data-for-visualization.json')
        except Exception as e:
            print("mail-data-for-visualization not found on s3")

        # Process email data
        process(inputpath, outputpath)

        # Let the queue know that the message is processed
        if completed:
            # Upload json file to s3 buckek
            s3.Object('quicksight.mlvisualizer.com',
                      'data/mail-data-for-visualization.json').put(
                Body=open('/home/ec2-user/scripts/temp/mail-data-for-visualization.json', 'rb'),
                ContentType='application/json')
            s3.meta.client.put_object_acl(ACL='public-read', Bucket='quicksight.mlvisualizer.com',
                                          Key='data/mail-data-for-visualization.json')
            message.delete()
            print("[Processed][" + target_key + "] SQS Message Deleted")

def main():
    SQSRetrieveMessage()


if __name__ == "__main__":
    main()



