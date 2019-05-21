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
    # TODO implement
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
    
    query_for_known=json.dumps({
        "query": {
            "bool": {
                "must": {
                    "term": {
                        "ImageKey": filename
                    }
                },
                "filter": {
                    "term": {
                        "is": "known"
                    }
                }
            }
        }
    })
    headers =  { "Content-Type" : "application/json" }
    
    print('BEFORE  RESPONSE')
    
    result = requests.post(target,headers=headers,data=query_for_known)
    
    res = result.json()
    
    print('AFTER RESPONSE')
    print('RESPONSE',res)
    
    size_query_for_known = len(res['hits']['hits'])
    
    print('size_query_for_known',size_query_for_known)

    if size_query_for_known > 0:
        faceId = res['hits']['hits'][0]['_source']['FaceId']
        indexId = res['hits']['hits'][0]['_id']
        
    faces=[]
    faces.apend(faceId)
    response=rekClient.delete_faces(CollectionId=collectionId,FaceIds=faces)
    print('Delete FaceId',response)
    
    

    response = known_table.delete_item(TableName = "ccKnownPeople",Key : { PersonID : faceId})
    print('Delete dynamo',response)
    
    target+="_delete/"+ indexId
    
    headers = { "Content-Type" : "application/json" }
    response_es = requests.post(target , data = json.dumps(json_doc) , headers=headers)
    print('Delete Elastic Search' , response_es)
    
    

