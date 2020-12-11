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
import threading


def does_log_group_exist(client, logGroup):

    response = client.describe_log_groups(
        logGroupNamePrefix=logGroup,
        limit=10
    )

    if(len(response['logGroups'])>0):
        return True
    else:
        return False

# Create CloudWatchEvents client
def log_result(message, logGroup, logStream):
    client = boto3.client('logs', region_name = "us-east-2")
    logStream+=("_"+str(threading.get_ident()))
    success = False

    if not does_log_group_exist(client, logGroup):
        response = client.create_log_group(logGroupName = logGroup)


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
            logResult(e,'LoggingError', 'LoggingErrorStream'+"_"+str(threading.get_ident()))
            continue

def retries(func):
    def wrapper_retries(*args, **kwargs):
        # if isinstance(args[-1],dict):
        #     print(args[-1])
        #     print(kwargs)
        attempts = 0
        result = None
        while True:
            try:
                result = func(*args,**kwargs)
                break
            except Exception as e:
                attempts +=1
                if attempts > 3:
                    raise
        return result


    return wrapper_retries
