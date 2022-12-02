import io
import json
import os

import aiohttp
import discord
import requests

from marsbots_eden.models import SourceSettings
from marsbots_eden.models import SignInCredentials


async def sign_in(
    gateway_url: str,
    credentials: SignInCredentials
):
    result = requests.post(gateway_url + "/sign_in", json=credentials.__dict__)
    check, error = await check_server_result_ok(result)
    if not check:
        raise Exception(error)
    authToken = result.json()['authToken']
    return authToken


async def request_creation(
    gateway_url: str,
    credentials: SignInCredentials,
    source: SourceSettings,
    config
):

    generator_name = config.generator_name
    config_dict = config.__dict__
    config_dict.pop("generator_name", None)

    auth_token = await sign_in(gateway_url, credentials)

    data = {
        "token": auth_token,
        "application": "discord", 
        "metadata": source.__dict__,
        "generator_name": generator_name, 
        "config": config_dict
    }    

    result = requests.post(gateway_url + "/request", json=data)
    check, error = await check_server_result_ok(result)

    if not check:
        raise Exception(error)

    task_id = result.content.decode("utf-8")

    return task_id


async def poll_creation_queue(
    gateway_url: str,
    minio_url: str,
    task_id: str,
    is_video_request: bool = False,
    prefer_gif: bool = True
):

    result = requests.post(gateway_url + "/fetch", json={"taskIds": [task_id]})

    check, error = await check_server_result_ok(result)
    if not check:
        raise Exception(error)

    result = json.loads(result.content)
    
    if not result:
        message_update = "_Server error: task ID not found_"
        raise Exception(message_update)

    result = result[0]
    file, sha = await get_file_update(result, minio_url, is_video_request, prefer_gif)

    return result, file, sha


async def get_file_update(result, minio_url, is_video_request=False, prefer_gif=True):
    status = result["status"]
    file = None
    sha = None
    if status == "complete" and is_video_request:
        sha = result["output"]
        sha_url = f"{minio_url}/{sha}"
        print("get a complete video")
        print(sha_url)        
        file = await get_video_clip_file(sha_url, gif=prefer_gif)
        print(file)
    elif status == "complete":
        sha = result["output"]
        sha_url = f"{minio_url}/{sha}"
        print("get a complete image")
        print(sha_url)
        file = await get_discord_file_from_url(sha_url, sha + ".png")
        print(img)
    elif "intermediate_outputs" in result:
        sha = result["intermediate_outputs"][-1]
        sha_url = f"{minio_url}/{sha}"
        print("get an intermediate image")
        print(sha_url)
        file = await get_discord_file_from_url(sha_url, sha + ".png")
        print(file)
    return file, sha


async def get_discord_file_from_url(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = io.BytesIO(await resp.read())
            print("get discord file", filename)
            discord_file = discord.File(data, filename)
            return discord_file


async def get_video_clip_file(sha_url, gif):
    sha_mp4 = sha_url.split("/")[-1]
    if not sha_mp4.endswith(".mp4"):
        sha_mp4 += ".mp4"
    sha_gif = sha_mp4.replace(".mp4", ".gif")
    
    print("get video clip")
    print(sha_mp4, sha_gif)
    # get_discord_file_from_url is giving a blank mp4 for some reason, so fall back to writing to disk
    res = requests.get(sha_url)
    with open(sha_mp4, "wb") as f:
        f.write(res.content)
    if gif:
        os.system(f"ffmpeg -i {sha_mp4} {sha_gif}")
        file_update = discord.File(sha_gif, sha_gif)
    else:
        file_update = discord.File(sha_mp4, sha_mp4)

    delete_file(sha_mp4)
    delete_file(sha_gif)

    return file_update


async def check_server_result_ok(result):
    if result.status_code != 200:
        error_message = result.content.decode("utf-8")
        error = f"_Server error: {error_message}_"
        return False, error
    return result.status_code == 200, None


def delete_file(path):
    if os.path.isfile(path):
        os.remove(path)
