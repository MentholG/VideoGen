import math
import os.path
import re
from os import path
import re
import requests
import json


from loguru import logger

from app.config import config
from app.models.schema import VideoParams, VoiceNames, VideoConcatMode
from app.services import llm, material, voice, video, subtitle
from app.models.exception import HttpException
from app.utils import utils
import boto3
from botocore.exceptions import NoCredentialsError

def detect_and_call(video_subject):
    # Regular expression to detect Twitter URL
    twitter_link_regex = r"https?://(?:www\.)?(twitter\.com|x\.com)/(?:#!/)?(\w+)/status/(\d+)"
    match = re.search(twitter_link_regex, video_subject)
    
    if match:
        # It's a Twitter link, extract the ID
        twitter_id = match.group(2)
        # Prepare API call
        url = "https://api.coze.com/open_api/v2/chat"
        headers = {
            'Authorization': 'Bearer pat_nHNJ5fqMDIQg8EcpcYfOT0oyaQzCIpk4k9v8uNWCltN34SckngHRKWEKrMw2xFuI',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': 'api.coze.com',
            'Connection': 'keep-alive'
        }
        data = {
            "conversation_id": "123",
            "bot_id": "7355685605986402309",
            "user": "29032201862555",
            "query": video_subject,
            "stream": False
        }
        logger.info(data)
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            # Assuming the API returns JSON
            response_data = response.json()
            # Extracting raw tweet information based on your example response
            logger.info(response_data)
            raw_content = response_data["messages"][1]["content"]
            raw_tweet_info = json.loads(raw_content)["data"]["text"]
            return raw_tweet_info
        else:
            return "API call failed with status code: {}".format(response.status_code)
    elif re.match(r"\d+", video_subject):
        # It's a Twitter ID, handle accordingly
        return "Detected a Twitter ID but this example does not make an API call for IDs."
    else:
        logger.info(f"Input is neither a Twitter link nor a Twitter ID.{video_subject}")
        return video_subject

# Example usage
# video_subject_example = "https://twitter.com/chiefaioffice/status/1770873353810714718"
# Uncomment the line below to test in your local environment where requests can be made.
# print(detect_and_call(video_subject_example))



def update_task_state(table, task_id, new_state):
    parts = task_id.split('_')
    if len(parts) != 2:
        raise HttpException(status_code=404, message=f"Task id is wrong format {task_id}")
    internal_task_id = parts[0]
    create_time = int(parts[1])
    response = table.update_item(
        Key={
            'task_id': internal_task_id,  # Assuming 'TaskID' is the primary key
            'create_time': create_time
        },
        UpdateExpression='SET #state = :val',  # Update the 'state' attribute
        ExpressionAttributeValues={
            ':val': new_state
        },
        ExpressionAttributeNames={
            '#state': 'state'  # Use if 'state' is a reserved word or for safer attribute naming
        },
        ReturnValues="UPDATED_NEW"
    )

def _parse_voice(name: str):
    # "female-zh-CN-XiaoxiaoNeural",
    # remove first part split by "-"
    if name not in VoiceNames:
        name = VoiceNames[0]

    parts = name.split("-")
    _lang = f"{parts[1]}-{parts[2]}"
    _voice = f"{_lang}-{parts[3]}"

    return _voice, _lang


async def start(task_id, table, params: VideoParams):
    """
    {
        "video_subject": "",
        "video_aspect": "横屏 16:9（西瓜视频）",
        "voice_name": "女生-晓晓",
        "enable_bgm": false,
        "font_name": "STHeitiMedium 黑体-中",
        "text_color": "#FFFFFF",
        "font_size": 60,
        "stroke_color": "#000000",
        "stroke_width": 1.5
    }
    """
    logger.info(f"start task: {task_id}")
    video_subject = detect_and_call(params.video_subject)
    voice_name, language = _parse_voice(params.voice_name)
    paragraph_number = params.paragraph_number
    n_threads = params.n_threads
    max_clip_duration = params.video_clip_duration

    logger.info("\n\n## generating video script")
    video_script = params.video_script.strip()
    if not video_script:
        video_script = llm.generate_script(video_subject=video_subject, language=params.video_language,
                                           paragraph_number=paragraph_number)
    else:
        logger.debug(f"video script: \n{video_script}")

    logger.info("\n\n## generating video terms")
    video_terms = params.video_terms
    if not video_terms:
        video_terms = llm.generate_terms(video_subject=video_subject, video_script=video_script, amount=5)
    else:
        if isinstance(video_terms, str):
            video_terms = [term.strip() for term in re.split(r'[,，]', video_terms)]
        elif isinstance(video_terms, list):
            video_terms = [term.strip() for term in video_terms]
        else:
            update_task_state(table=table, task_id=task_id, new_state="FAIL")
            raise ValueError("video_terms must be a string or a list of strings.")

        logger.debug(f"video terms: {utils.to_json(video_terms)}")

    script_file = path.join(utils.task_dir(task_id), f"script.json")
    script_data = {
        "script": video_script,
        "search_terms": video_terms
    }

    with open(script_file, "w", encoding="utf-8") as f:
        f.write(utils.to_json(script_data))

    logger.info("\n\n## generating audio")
    audio_file = path.join(utils.task_dir(task_id), f"audio.mp3")
    sub_maker = await voice.tts(text=video_script, voice_name=voice_name, voice_file=audio_file)
    if sub_maker is None:
        logger.error(
            "failed to generate audio, maybe the network is not available. if you are in China, please use a VPN.")
        update_task_state(table=table, task_id=task_id, new_state="FAIL")
        return

    audio_duration = voice.get_audio_duration(sub_maker)
    audio_duration = math.ceil(audio_duration)

    subtitle_path = ""
    if params.subtitle_enabled:
        subtitle_path = path.join(utils.task_dir(task_id), f"subtitle.srt")
        subtitle_provider = config.app.get("subtitle_provider", "").strip().lower()
        logger.info(f"\n\n## generating subtitle, provider: {subtitle_provider}")
        subtitle_fallback = False
        if subtitle_provider == "edge":
            voice.create_subtitle(text=video_script, sub_maker=sub_maker, subtitle_file=subtitle_path)
            if not os.path.exists(subtitle_path):
                subtitle_fallback = True
                logger.warning("subtitle file not found, fallback to whisper")
            else:
                subtitle_lines = subtitle.file_to_subtitles(subtitle_path)
                if not subtitle_lines:
                    logger.warning(f"subtitle file is invalid, fallback to whisper : {subtitle_path}")
                    subtitle_fallback = True

        # if subtitle_profiler == "polly"  or subtitle_fallback:
        #     subtitle.create(audio_file=audio_file, subtitle_file=subtitle_path)
        #     logger.info("\n\n## correcting subtitle")
        #     subtitle.correct(subtitle_file=subtitle_path, video_script=video_script)
        
        if subtitle_provider == "whisper" or subtitle_fallback:
            subtitle.create(audio_file=audio_file, subtitle_file=subtitle_path)
            logger.info("\n\n## correcting subtitle")
            subtitle.correct(subtitle_file=subtitle_path, video_script=video_script)


        subtitle_lines = subtitle.file_to_subtitles(subtitle_path)
        if not subtitle_lines:
            logger.warning(f"subtitle file is invalid: {subtitle_path}")
            subtitle_path = ""

    logger.info("\n\n## downloading videos")
    downloaded_videos = material.download_videos(task_id=task_id,
                                                 search_terms=video_terms,
                                                 video_aspect=params.video_aspect,
                                                 video_contact_mode=params.video_concat_mode,
                                                 audio_duration=audio_duration * params.video_count,
                                                 max_clip_duration=max_clip_duration,
                                                 )
    if not downloaded_videos:
        logger.error(
            "failed to download videos, maybe the network is not available. if you are in China, please use a VPN.")
        update_task_state(table=table, task_id=task_id, new_state="FAIL")
        return

    final_video_paths = []
    object_names = []
    video_concat_mode = params.video_concat_mode
    if params.video_count > 1:
        video_concat_mode = VideoConcatMode.random

    for i in range(params.video_count):
        index = i + 1
        combined_video_path = path.join(utils.task_dir(task_id), f"combined-{index}.mp4")
        logger.info(f"\n\n## combining video: {index} => {combined_video_path}")
        video.combine_videos(combined_video_path=combined_video_path,
                             video_paths=downloaded_videos,
                             audio_file=audio_file,
                             video_aspect=params.video_aspect,
                             video_concat_mode=video_concat_mode,
                             max_clip_duration=max_clip_duration,
                             threads=n_threads)

        final_video_path = path.join(utils.task_dir(task_id), f"final-{index}.mp4")

        logger.info(f"\n\n## generating video: {index} => {final_video_path}")
        # Put everything together
        video.generate_video(video_path=combined_video_path,
                             audio_path=audio_file,
                             subtitle_path=subtitle_path,
                             output_file=final_video_path,
                             params=params,
                             )
        final_video_paths.append(final_video_path)
        object_names.append(f"{task_id}")

    logger.success(f"task {task_id} finished, generated {len(final_video_paths)} videos.")
    upload_files_to_s3(final_video_paths, 'laoguis3-us-east-1', 'us-east-1', object_names)
    update_task_state(table=table, task_id=task_id, new_state="SUCCESS")

    return {
        "videos": final_video_paths,
    }


def upload_files_to_s3(file_names, bucket, region, object_names=None):
    """
    Upload multiple files to an S3 bucket in a specified region

    :param file_names: List of files to upload
    :param bucket: Bucket to upload to
    :param region: AWS region where the bucket is located
    :param object_names: List of S3 object names. If not specified, file_names are used
    :return: None
    """
    
    # Initialize the S3 client
    s3_client = boto3.client('s3', region_name=region)
    
    # Iterate over the list of file names
    for i, file_name in enumerate(file_names):
        # Use the file name as the object name if not specified
        # dir_name, file_name = os.path.split(file_name)
        object_name = object_names[i] if object_names is not None else file_name
        object_name = os.path.join('videos', object_name+".mp4")
        
        try:
            s3_client.upload_file(file_name, bucket, object_name)
            print(f"[upload_files_to_s3] {file_name} uploaded successfully to {bucket}/{object_name}")
        except NoCredentialsError:
            print("[upload_files_to_s3] Credentials not available for", file_name)
        except Exception as e:
            print(f"[upload_files_to_s3] Failed to upload {file_name}: {e}")