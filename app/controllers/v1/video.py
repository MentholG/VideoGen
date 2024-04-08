from os import path

from fastapi import BackgroundTasks, Request, Depends, Path
from loguru import logger

from datetime import datetime

from app.controllers import base
from app.controllers.v1.base import new_router
from app.models.exception import HttpException
from app.models.schema import TaskVideoRequest, TaskQueryResponse, TaskResponse, TaskQueryRequest
from app.services import task as tm
from app.utils import utils

import boto3

# 认证依赖项
# router = new_router(dependencies=[Depends(base.verify_token)])
router = new_router()

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('task')  # Replace 'YourTableName' with your actual table name


@router.post("/videos", response_model=TaskResponse, summary="Generate short video from a theme")
async def create_video(request: Request, body: TaskVideoRequest, background_tasks: BackgroundTasks):
    internal_task_id = utils.get_uuid()
    create_time = int(datetime.now().timestamp())  # Current timestamp as sort key
    task_id = "_".join([internal_task_id, str(create_time)])
    request_id = utils.get_uuid()  # or any method you use to generate a unique request ID
    
    try:
        internal_task = {
            "task_id": internal_task_id,
            "create_time": create_time,
            # Add other task details you need to store
            "state": "RUNNING"
        }
        
        # Insert task into DynamoDB
        table.put_item(Item=internal_task)
        logger.success(f"Video created and task stored in DynamoDB: {internal_task}")
        body_dict = body.dict()
        internal_task.update(body_dict)
        background_tasks.add_task(tm.start, task_id=task_id, table=table, params=body)
        # result = tm.start(task_id=task_id, table=table, params=body)
        # task["result"] = result
        task = {
            "task_id": task_id,
            "create_time": create_time,
            # Add other task details you need to store
            "state": "RUNNING"
        }

        logger.success(f"video creating: {utils.to_json(task)}")
        
        return utils.get_response(200, task)
    except Exception as e:
        logger.error(f"Failed to create video task: {str(e)}")
        raise HttpException(task_id=task_id, status_code=400, message=f"request {request_id}: {str(e)}")

@router.get("/tasks/{task_id}", response_model=TaskQueryResponse, summary="Query task status")
async def get_task(request: Request, task_id: str = Path(..., description="任务ID"),
                    query: TaskQueryRequest = Depends()):
    try:
        request_id = base.get_task_id(request)
        data = query.dict()
        parts = task_id.split('_')
        if len(parts) != 2:
            raise HttpException(task_id=task_id, status_code=404, message=f"task id is wrong format {task_id}")
        internal_task_id = parts[0]
        create_time = int(parts[1])

        data["task_id"] = task_id
        # Fetch task from DynamoDB
        logger.info(f"try retriving task id: {task_id}")
        response = table.get_item(
            Key={
                'task_id': internal_task_id,
                'create_time': create_time
            }
        )
        task = response.get('Item')
        
        if not task:
            raise HttpException(task_id=task_id, status_code=404, message=f"task not found {task_id}")
        
        return utils.get_response(200, task, "Task retrieved successfully.")
    except Exception as e:
        logger.error(f"Failed to retrieve task: {str(e)}")
        raise HttpException(task_id=task_id, status_code=404,
                            message=f"request {request_id}: task not found", data=data)