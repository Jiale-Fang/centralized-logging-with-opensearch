# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import uuid
import json
import gzip
import copy
import types
import base64
import pytest
from typing import Union
from boto3.dynamodb.conditions import ConditionBase, Attr, Key
from test.mock import mock_iam_context, mock_sqs_context, mock_ddb_context, default_environment_variables


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_available_services(mock_iam_context, mock_sqs_context, mock_ddb_context):
    from metadata_writer.lambda_function import available_services
    
    assert 'ec2' in available_services()
    assert 'scheduler' in available_services()
    assert 'events' in available_services()


def test_check_scheduler_services(mock_iam_context, mock_sqs_context, mock_ddb_context):
    from metadata_writer.lambda_function import check_scheduler_services, AWS_DDB_META, AWS_IAM
    
    partition = AWS_DDB_META.get(meta_name='Partition')['value']
    region = AWS_DDB_META.get(meta_name='Region')['value']
    account_id = AWS_DDB_META.get(meta_name='AccountId')['value']
    pipeline_resources_builder_schedule_policy_arn = AWS_DDB_META.get(meta_name='PipelineResourcesBuilderSchedulePolicy')['arn']
    policy_document = {
        'Sid': 'EventBridgeScheduler',
        'Effect': 'Allow',
        'Action': [
            "scheduler:GetSchedule",
            "scheduler:UpdateSchedule",
            "scheduler:CreateSchedule",
            "scheduler:GetScheduleGroup",
            "scheduler:DeleteScheduleGroup",
            "scheduler:CreateScheduleGroup",
            "scheduler:DeleteSchedule",
            "scheduler:TagResource",
        ], 
        'Resource': [
            f'arn:{partition}:scheduler:{region}:{account_id}:schedule/*/*',
            f'arn:{partition}:scheduler:{region}:{account_id}:schedule-group/*',
        ],
        }
    
    # test china region
    for cn_region in ('cn-north-1', 'cn-northwest-1'):
        AWS_DDB_META.put(meta_name='Region', item={'value': cn_region})
        
        check_scheduler_services()
        available_services_list = AWS_DDB_META.get(meta_name='AvailableServices')
        assert 'scheduler' not in available_services_list['value']
        assert 'events' in available_services_list['value']
        
        for meta_name in ('LogProcessorStartExecutionRole', 'LogMergerStartExecutionRole', 'LogArchiveStartExecutionRole'):
            role_name = AWS_DDB_META.get(meta_name=meta_name)['name']
            response = AWS_IAM.get_role(role_name=role_name)
            assert response['Role']['AssumeRolePolicyDocument']['Statement'] == [{'Effect': 'Allow', 'Principal': {'Service': ['lambda.amazonaws.com']}, 'Action': ['sts:AssumeRole']}]
        assert policy_document not in AWS_IAM.get_policy_document(arn=pipeline_resources_builder_schedule_policy_arn)['Document']['Statement']
    
    # test other region
    AWS_DDB_META.put(meta_name='Region', item={'value': region})
    check_scheduler_services()
    available_services_list = AWS_DDB_META.get(meta_name='AvailableServices')
    assert 'scheduler' in available_services_list['value']
    assert 'events' in available_services_list['value']
    
    for meta_name in ('LogProcessorStartExecutionRole', 'LogMergerStartExecutionRole', 'LogArchiveStartExecutionRole'):
        role_name = AWS_DDB_META.get(meta_name=meta_name)['name']
        response = AWS_IAM.get_role(role_name=role_name)
        assert {'Effect': 'Allow', 'Principal': {'Service': 'scheduler.amazonaws.com'}, 'Action': 'sts:AssumeRole'} in response['Role']['AssumeRolePolicyDocument']['Statement'] 
    assert policy_document in AWS_IAM.get_policy_document(arn=pipeline_resources_builder_schedule_policy_arn)['Document']['Statement']

    
def test_lambda_handler(mock_iam_context, mock_sqs_context, mock_ddb_context):
    from metadata_writer.lambda_function import lambda_handler, AWS_DDB_META, AWS_IAM
    
    account_id = os.environ['ACCOUNT_ID']
    meta_name = str(uuid.uuid4())
    metadata_writer_event = {
        'RequestType': 'Create', 
        'ResourceProperties': {
            'Items': [
                {
                    'metaName': meta_name, 
                    'service': 'AWS', 
                    'name': account_id, 
                    'arn': ''
                    }
                ]
            }
        }
    context = types.SimpleNamespace()
    
    # test create
    with pytest.raises(Exception) as exception_info:
        lambda_handler(event='not-a-dict', _=context)
    assert exception_info.value.args[0] == 'The event is not a dict.'
    
    item_count = AWS_DDB_META.scan_count()
    event = copy.deepcopy(metadata_writer_event)
    event['ResourceProperties'].pop('Items', None)
    
    lambda_handler(event=event, _=context)
    assert AWS_DDB_META.scan_count() == item_count
    
    event = copy.deepcopy(metadata_writer_event)
    lambda_handler(event=event, _=context)
    assert AWS_DDB_META.get(meta_name=meta_name) == {
        'metaName': meta_name, 
        'service': 'AWS', 
        'name': account_id, 
        'arn': ''
        }
    
    available_services_list = AWS_DDB_META.get(meta_name='AvailableServices')
    assert 'ec2' in available_services_list['value']
    assert 'scheduler' in available_services_list['value']
    assert 'events' in available_services_list['value']
    
    for meta_name in ('LogProcessorStartExecutionRole', 'LogMergerStartExecutionRole', 'LogArchiveStartExecutionRole'):
        role_name = AWS_DDB_META.get(meta_name=meta_name)['name']
        response = AWS_IAM.get_role(role_name=role_name)
        assert {'Effect': 'Allow', 'Principal': {'Service': 'scheduler.amazonaws.com'}, 'Action': 'sts:AssumeRole'} in response['Role']['AssumeRolePolicyDocument']['Statement'] 
    
    # test delete
    meta_name = 'TEST-DELETE'
    create_event = copy.deepcopy(metadata_writer_event)
    create_event['ResourceProperties']['Items'][0]['metaName'] = meta_name
    lambda_handler(event=create_event, _=context)
    assert AWS_DDB_META.get(meta_name=meta_name) == {
        'metaName': meta_name, 
        'service': 'AWS', 
        'name': account_id, 
        'arn': ''
        }
    
    delete_event = copy.deepcopy(create_event)
    delete_event['RequestType'] = 'Delete'
    lambda_handler(event=delete_event, _=context)
    assert AWS_DDB_META.get(meta_name=meta_name) is None
    
