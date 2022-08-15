import io
import json
import os

import aiohttp
import discord
import requests

from marsbots_eden.models import SourceSettings


async def request_creation(
    gateway_url: str,
    source: SourceSettings,
    config,
):
    generator_name = config.generator_name
    config_dict = config.__dict__
    config_dict.pop("generator_name", None)

    data = {
        "source": source.__dict__,
        "generator_name": generator_name,
        "config": config_dict,
    }

    result = requests.post(gateway_url + "/request_creation", json=data)
    check, error = await check_server_result_ok(result)

    if not check:
        raise Exception(error)

    result = json.loads(result.content)
    print(result)
    task_id = result["task_id"]
    return task_id


async def poll_creation_queue(
    gateway_url: str,
    minio_url: str,
    task_id: str,
    is_video_request: bool = False,
):
    result = requests.post(gateway_url + "/get_creations", json={"task": task_id})

    check, error = await check_server_result_ok(result)
    if not check:
        raise Exception(error)

    result = json.loads(result.content)

    if not result:
        message_update = "_Server error: task ID not found_"
        raise Exception(message_update)

    result = result[0]
    file = await get_file_update(result, minio_url, is_video_request)

    return result, file


async def get_file_update(result, minio_url, is_video_request=False):
    status = result["status"]
    file = None
    if status == "complete" and is_video_request:
        sha = result["video_sha"]
        print(sha)
        sha_url = f"{minio_url}/{sha}"
        print(sha_url)
        file = await get_video_clip_file(sha_url, gif=True)
    elif status == "complete":
        sha = result["sha"]
        sha_url = f"{minio_url}/{sha}"
        file = await get_discord_file_from_url(sha_url, sha + ".png")
    elif "intermediate_sha" in result:
        sha = result["intermediate_sha"][-1]
        sha_url = f"{minio_url}/{sha}"
        file = await get_discord_file_from_url(sha_url, sha + ".png")
    return file


async def get_discord_file_from_url(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = io.BytesIO(await resp.read())
            discord_file = discord.File(data, filename)
            return discord_file


async def get_video_clip_file(sha_url, gif):
    sha_mp4 = sha_url.split("/")[-1]
    sha_gif = sha_mp4.replace(".mp4", ".gif")
    if gif:
        res = requests.get(sha_url)
        with open(sha_mp4, "wb") as f:
            f.write(res.content)
        os.system(f"ffmpeg -i {sha_mp4} {sha_gif}")
        file_update = discord.File(sha_gif, sha_gif)
    else:
        file_update = await get_discord_file_from_url(sha_url, sha_mp4)
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
