import boto3

def lambda_handler(event,context):
    bucket='face-collection-criminal'
    collectionId='Face-Collection-Criminal'
    fileName='shubham-test.jpeg'
    threshold = 50
    maxFaces=1

    client=boto3.client('rekognition')
  
    response=client.search_faces_by_image(CollectionId=collectionId,
                                Image={'S3Object':{'Bucket':bucket,'Name':fileName}},
                                FaceMatchThreshold=threshold,
                                MaxFaces=maxFaces)

    print('Response',response)           
    faceMatches=response['FaceMatches']
    print ('Matching faces')
    for match in faceMatches:
            print ('FaceId:' + match['Face']['FaceId'])
            print ('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
            print
