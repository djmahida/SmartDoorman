import json
import boto3
from botocore.vendored import requests
import logging
import base64
from boto3.dynamodb.conditions import Key, Attr
import random

def lambda_handler(event, context):
    # TODO implement
    logging.info("API CALLED. EVENT IS:{}".format(event))
    
    print(event)
    print("Kinesis data is")
    data = event['Records'][0]['kinesis']['data']
    print(base64.b64decode(data))
    json_data = json.loads(base64.b64decode(data).decode('utf-8'))
    
    print('JSON DATA',data)
    
    dynamodb = boto3.resource('dynamodb')
    criminal_table = dynamodb.Table('ccCriminal')
    known_table = dynamodb.Table('ccKnownPeople')
    smsClient = boto3.client('sns')
    owner_mobile = "**********"
    
    sqsClient = boto3.resource('sqs')
    global_queue = sqsClient.get_queue_by_name(QueueName = "GlobalVariable")

    for message in global_queue.receive_messages(MaxNumberOfMessages=10):
        message_from_queue = message.body.split(":")
        name_message_from_queue = message_from_queue[0]
        value_message_from_queue = message_from_queue[1]
        
        if name_message_from_queue=="criminal" and value_message_from_queue=="true":
            print(name_message_from_queue , value_message_from_queue)
            return
        if name_message_from_queue=="known" and value_message_from_queue=="true":
            print(name_message_from_queue , value_message_from_queue)    
            return
        if name_message_from_queue=="visitor" and value_message_from_queue=="true":
            print(name_message_from_queue , value_message_from_queue)
            return

                
    url = "YOUR URL"
    index = "global/"
    type = "record/"
    
    target = url + index + type +"_search"
    
    
    
    try:

        face_search_response = json_data['FaceSearchResponse']
        if face_search_response is None:
            return ("No one at the door")
        else:
            matched_face = json_data['FaceSearchResponse'][0]['MatchedFaces']
        
        if face_search_response is not None and matched_face is None:
            messageToSMS = "The person at the door is unknown and safe."
            var_name = "visitor"
            var_value = "true"
            response = global_queue.send_message(
            MessageBody = var_name + ":" +var_value
            )
            mobile = owner_mobile
            
        else:
            image_id = json_data['FaceSearchResponse'][0]['MatchedFaces'][0]['Face']['ImageId']
            print('IMAGEID',image_id)
            face_id = json_data['FaceSearchResponse'][0]['MatchedFaces'][0]['Face']['FaceId']
            print('FACEID',face_id)
            name_of_person = json_data['FaceSearchResponse'][0]['MatchedFaces'][0]['Face']['ExternalImageId']
            
            
            query_for_known=json.dumps({
                "query": {
                    "bool": {
                        "must": {
                            "term": {
                                "ImageKey": name_of_person
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
                password = random.randint(1111,9999)
                name = name_of_person.split(".")[0]
                print('NAME',name)
                
                sqsClient = boto3.resource('sqs')
                queue = sqsClient.get_queue_by_name(QueueName = "AuthenticateKnownUsers")
                
                response = queue.send_message(
                MessageBody = name+":"+str(password)
                )
                
                var_name = "known"
                var_value = "true"
                response2 = global_queue.send_message(
                MessageBody = var_name +":"+ var_value
                )
                
                
                
                table_response = known_table.scan(
                FilterExpression=Key('ImageKey').eq(name_of_person)
                )
                print('table response',table_response)
                response_json = json.loads(json.dumps(table_response['Items']))
                print('response json',response_json)
                
                email = response_json[0]['Email']
                known_name = response_json[0]['Name']
                relation = response_json[0]['Relation']
                
                messageToSMS = "YOU ARE IDENTIFIED AS "+known_name+"\n"
                messageToSMS += "Your Password is :" +str(password)+"\n"
                messageToSMS += "Please Enter it inside the application and submit it."
                
                SENDER = "**********"
                RECIPIENT = email
                AWS_REGION = "us-east-1"
                SUBJECT = " Password for Accessing "
                BODY_TEXT = messageToSMS
                BODY_HTML = "<html><head></head><body><h1><font color='red'>Password For Accessing</font></h1><p>You are Identified as {}. Your Password is {}. Please Enter it inside the application and submit it <p></body></html>".format(known_name,password)
                CHARSET = "UTF-8"
                
            
            else:
                var_name="criminal"
                var_value = "true"
                response = global_queue.send_message(
                MessageBody = var_name + ":"+var_value
                )
                name_criminal = name_of_person.split(".")[0]
                table_response = criminal_table.scan(
                FilterExpression=Key('ImageKey').eq(name_of_person)
                )
                print('table response',table_response)
                response_json = json.loads(json.dumps(table_response['Items']))
                print('response json',response_json)
                
                criminal_name = response_json[0]['Name']
                crime = response_json[0]['Crime']
                severity = response_json[0]['severity']
                
                
                messageToSMS = "Alert! Call 911! The person at the door is a criminal- Name: {} Crime: {} Severity: {}".format(criminal_name,crime,severity) + "\n"
                mobile = owner_mobile
                SENDER = "***********"
                RECIPIENT = "***********"
                AWS_REGION = "us-east-1"
                SUBJECT = " ALERT ALERT !! "
                BODY_TEXT = messageToSMS
                BODY_HTML = "<html><head></head><body><h1><font color='red'>ALERT ALERT !! </font></h1><p>Alert! Call 911! The person at the door is a criminal- Name: {} Crime: {} Severity: {} <p></body></html>".format(criminal_name,crime,severity)
                CHARSET = "UTF-8"
                
            # person_information  = table.scan(
            #     FilterExpression=Key('CriminalId').eq(image_id)
            # )
            # name=person_information.Name
            # severity=person_information.severity
            # location=person_information.location
            # crime=person_information.Crime
            
        # smsClient.publish(
        #     PhoneNumber = mobile,
        #     Message=messageToSMS
        #         )
        
        client = boto3.client('ses',region_name=AWS_REGION)
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER
        )
                
        print("MESSAGE TO",mobile)   
    
    except:
        print('Exception')
        
                
