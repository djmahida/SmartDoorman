import json
import boto3
import random
import json
import botocore.vendored.requests as requests
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from botocore.vendored import requests

url = "ENTER YOUR URL"
index = "global/"
type = "record/"

target = url + index + type


def lambda_handler(event, context):
    print('Event',event)
    
    filename = event['Records'][0]['s3']['object']['key']
    
    print('Inside Handler')
    
    collectionId='Face-Collection-Criminal'
    threshold = 50
    maxFaces=1

    rekClient=boto3.client('rekognition')
    s3_client = boto3.client('s3')
    bucket_name = "face-collection-known"
    
    #key_array = ['1.jpg','2.jpg','3.jpeg','4.jpeg','5.jpeg','6.jpg','7.jpg','8.jpg','9.png']
    #key_array=['10.jpeg']
    
    dynamo_client = boto3.resource('dynamodb',region_name='us-east-1')
    known_table = dynamo_client.Table('ccKnownPeople')
    

    name = filename.split('.')[0]

    print('key',name[0])
    
    response=rekClient.index_faces(CollectionId=collectionId,
    Image={
    'S3Object':
    {
    'Bucket':bucket_name,
    'Name':filename
    } 
    },
    ExternalImageId=filename,
    DetectionAttributes=['ALL'])
    
    print('New Response',response)
    
    for faceRecord in response['FaceRecords']:
         faceId = faceRecord['Face']['FaceId']

    response = known_table.put_item(
    Item={
    "Name": filename.split('.')[0],
    "Relation" : "RELATION WITH YOU",
    "Email" : "YOUR EMAIL",
    "PersonID" : faceId,
    "ImageKey" : filename,
    "AccessLevel" : random.randint(1,5)
    } 
    )
    
    json_doc = {
    "ImageKey" : filename,
    "FaceId" : faceId,
    "is" : "known"
    }
    
    
    headers = { "Content-Type" : "application/json" }
    response_es = requests.post(target , data = json.dumps(json_doc) , headers=headers)
    print('Response Elastic Search' , response_es)
    
    
    
    print('Response Dynamo',response)
