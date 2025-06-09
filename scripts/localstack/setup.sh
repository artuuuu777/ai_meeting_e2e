#!/bin/bash

# Wait for LocalStack to be ready
sleep 10

# Create S3 buckets
awslocal s3 mb s3://meeting-ai-dev-raw-audio
awslocal s3 mb s3://meeting-ai-dev-processed-data
awslocal s3 mb s3://meeting-ai-dev-logs

# Create SQS queues
awslocal sqs create-queue --queue-name meeting-ai-dev-audio-processing
awslocal sqs create-queue --queue-name meeting-ai-dev-audio-processing-dlq

echo "LocalStack setup completed"