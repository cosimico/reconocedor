import boto3
import json

def lambda_handler(event, context):
    # Cliente de Rekognition y S3
    client = boto3.client('rekognition')
    s3_client = boto3.client('s3')

    bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # Lógica para determinar los nombres de las imágenes
    source_image = object_key
    target_image = object_key.replace('.jpg', '_target.jpg')

    # Verifica si el archivo objetivo existe
    try:
        s3_client.head_object(Bucket=bucket, Key=target_image)
    except s3_client.exceptions.NoSuchKey:
        return {
            'statusCode': 200,
            'body': json.dumps("Esperando la segunda imagen...")
        }

    # Realiza la comparación
    response = client.compare_faces(
        SourceImage={'S3Object': {'Bucket': bucket, 'Name': source_image}},
        TargetImage={'S3Object': {'Bucket': bucket, 'Name': target_image}},
        SimilarityThreshold=80
    )

    # Analiza y guarda la respuesta
    result = "Las imágenes no contienen la misma persona."
    for faceMatch in response.get('FaceMatches', []):
        similarity = faceMatch['Similarity']
        result = f"Las imágenes {source_image} y {target_image}  contienen la misma persona con una similitud del {similarity}%."

    # Escribe la respuesta en un archivo
    output_file = f'result-{object_key}.txt'
    s3_client.put_object(Bucket=bucket, Key=output_file, Body=result)

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
