import json
import boto3
import random
import json
import botocore.vendored.requests as requests
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from botocore.vendored import requests

url = "YOUR URL"
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
    bucket_name = "face-collection-criminal"
    
    dynamo_client = boto3.resource('dynamodb',region_name='us-east-1')
    criminal_table = dynamo_client.Table('ccCriminal')
    
    crime_array = ['felony','murder','rape','sexual-assault','kidnapping','smuggling','homicide', 'accident']
    location_array = ['New York City', 'Los Angeles' , 'San Fransisco' , 'Las Vegas' , 'Jersey City', 'Seattle']
    name_array = ['criminal 1','criminal 2','criminal 3','criminal 4','criminal 5','criminal 6','criminal 7','criminal 8','criminal 9']
    
    severity = {
        'felony' : "1" ,
        'murder' : "5",
        'rape' : "3",
        'sexual-assault' : "2",
        'kidnapping' : "3",
        'smuggling' : "5",
        'homicide' : "5",
        'accident' : "2"
    }
    
    print('key',filename)
    
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
                            
    age = random.randint(30,90)
    crime = random.choice(crime_array)
    location = random.choice(location_array)

    response = criminal_table.put_item(
    Item={
    "Name": filename.split('.')[0],
    "Age" : str(age),
    "Crime" :       crime,
    "CriminalId":  faceId,
    "ImageKey" : filename ,
    "location" :   location  ,
    "severity" :  severity[crime]  
    } 
    
    )
    
    json_doc = {
    "ImageKey" : filename,
    "FaceId" : faceId,
    "is": "criminal"
    }
    
    
    headers = { "Content-Type" : "application/json" }
    response_es = requests.post(target , data = json.dumps(json_doc) , headers=headers)
    print('Response Elastic Search' , response_es)
    
    
    
    print('Response Dynamo',response)
