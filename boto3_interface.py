# Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import json
from datetime import datetime
import boto3
import botocore
import time


# Create CloudWatchEvents client
def log_result(message, logGroup, logStream):
    client = boto3.client('logs', region_name = "us-east-2")
    success = False
    while not success:
        try:
            response = client.describe_log_streams(
                logGroupName=logGroup,
                logStreamNamePrefix=logStream,
            )

            print(response)

            sequence_token = response['logStreams'][0].get('uploadSequenceToken',)

            timestamp = int(round(time.time() * 1000))
            message = str(message)

            if sequence_token:
                print("The sequence token is ", sequence_token)
                response = client.put_log_events(
                    logGroupName=logGroup,
                    logStreamName=logStream,
                    logEvents=[
                        {
                            'timestamp': timestamp,
                            'message': message
                        },
                    ],
                    sequenceToken = sequence_token
                )
            else:
                response = client.put_log_events(
                    logGroupName=logGroup,
                    logStreamName=logStream,
                    logEvents=[
                        {
                            'timestamp': timestamp,
                            'message': message
                        },
                    ],
                )

            success = True
            print(response)

        except IndexError as e:
            print(e)
            response = client.create_log_stream(logGroupName = logGroup, logStreamName = logStream)
            continue
        except Exception as e:
            print(e)
            response = client.create_log_group(logGroupName = logGroup)
            continue
