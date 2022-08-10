import asyncio
import os
import io
import json

import aiohttp
import discord
import requests

from marsbots_eden.models import SourceSettings


async def generation_loop(
    gateway_url: str,
    minio_url: str,
    ctx: discord.ApplicationContext,
    start_bot_message: str,
    source: SourceSettings,
    config,
    refresh_interval: int,
):

    generator_name = config.generator_name
    config_dict = config.__dict__
    config_dict.pop("generator_name", None)

    data = {
        "source": source.__dict__,
        "generator_name": generator_name,
        "config": config_dict
    }
    print(data)

    result = requests.post(gateway_url + "/request_creation", json=data)

    check, error = await check_server_result_ok(result)
    if not check:
        await edit_interaction(ctx, start_bot_message, error)
        return

    result = json.loads(result.content)
    task_id = result["task_id"]
    current_sha = None

    while True:
        result = requests.post(gateway_url + "/get_creations", json={"task": task_id})

        check, error = await check_server_result_ok(result)
        if not check:
            await edit_interaction(ctx, start_bot_message, error)
            return

        result = json.loads(result.content)

        if not result:
            message_update = "_Server error: task ID not found_"
            await edit_interaction(ctx, start_bot_message, message_update)
            return

        result = result[0]
        status = result["status"]

        message_update = ""
        file_update = None

        # update message string
        if status == "failed":
            message_update += "_Server error: Eden task failed_"
        elif status in "pending":
            message_update += "_Creation is pending_"
        elif status == "queued":
            queue_idx = result["status_code"]
            message_update += f"_Creation is #{queue_idx} in queue_"
        elif status == "running":
            progress = result["status_code"]
            message_update += f"_Creation is **{progress}%** complete_"
        elif status == "complete":
            message_update += ""

        # update message image
        if status == "complete" or "intermediate_sha" in result:
            video_clip = False
            if status == 'complete':
                if 'video_sha' in result:
                    last_sha = result['video_sha']
                    video_clip = True
                else:
                    last_sha = result['sha']
            else:
                last_sha = result['intermediate_sha'][-1]
            if last_sha != current_sha:
                current_sha = last_sha                
                if video_clip:
                    message_update_gif = "_Creation is complete. Making GIF..._"
                    await edit_interaction(ctx, start_bot_message, message_update_gif, None)
                    sha_url = f'{minio_url}/{current_sha}.mp4'
                    file_update = await get_video_clip_file(sha_url, gif=True)
                else:
                    sha_url = f'{minio_url}/{current_sha}'
                    filename = f'{current_sha}.png'
                    file_update = await get_discord_file_from_url(sha_url, filename)
        
        # finish up
        await edit_interaction(ctx, start_bot_message, message_update, file_update)
        
        if status not in ["queued", "pending", "running"]:
            break
        
        await asyncio.sleep(refresh_interval)


async def edit_interaction(ctx, start_bot_message, message_update, file_update=None):
    message_content = f"{start_bot_message}\n{message_update}"
    if file_update:
        await ctx.edit(content=message_content, file=file_update)
    else:
        await ctx.edit(content=message_content)


async def get_discord_file_from_url(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = io.BytesIO(await resp.read())
            discord_file = discord.File(data, filename)
            return discord_file


async def get_video_clip_file(sha_url, gif):
    sha_mp4 = sha_url.split('/')[-1]
    sha_gif = sha_mp4.replace('.mp4', '.gif')
    if gif:
        res = requests.get(sha_url)
        with open(sha_mp4, "wb") as f:
            f.write(res.content)
        os.system(f'ffmpeg -i {sha_mp4} {sha_gif}')
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