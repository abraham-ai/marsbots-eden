import asyncio
import io
import json
from dataclasses import dataclass
from dataclasses import field
from typing import List

import aiohttp
import discord
import requests


@dataclass
class SourceSettings:
    origin: str
    author: int
    author_name: str
    guild: int
    guild_name: str
    channel: int
    channel_name: str


@dataclass
class EdenClipXSettings:
    text_input: str
    image_url: str = ""
    step_multiplier: float = 1.0
    color_target_pixel_fraction: float = 0.75
    color_loss_f: float = 0.0
    color_rgb_target: tuple[float] = (0.0, 0.0, 0.0)
    image_weight: float = 0.35
    n_permuted_prompts_to_add: int = -1
    width: int = 0
    height: int = 0
    num_octaves: int = 3
    octave_scale: float = 2.0
    clip_model_options: List = field(
        default_factory=lambda: [["ViT-B/32", "ViT-B/16", "RN50"]],
    )
    num_iterations: tuple[int] = (100, 200, 300)


@dataclass
class StableDiffusionSettings:
    text_input: str
    width: int
    height: int
    ddim_steps: int
    plms: bool
    C: int
    f: int


@dataclass
class OracleSettings:
    text_input: str


async def generation_loop(
    gateway_url,
    minio_url,
    ctx,
    start_bot_message,
    source,
    config,
    refresh_interval: int,
):
    generator_names = {
        EdenClipXSettings: "eden-clipx",
        StableDiffusionSettings: "stable-diffusion",
        OracleSettings: "oracle",
    }

    generator_name = generator_names[type(config)]
    data = {
        "source": source.__dict__,
        "generator_name": generator_name,
        "config": config.__dict__,
    }
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
            if status == "complete":
                last_sha = result["sha"]
            else:
                last_sha = result["intermediate_sha"][-1]
            if last_sha != current_sha:
                current_sha = last_sha
                sha_url = f"{minio_url}/{current_sha}"
                filename = f"{current_sha}.png"
                file_update = await get_discord_file_from_url(sha_url, filename)

        if status not in ["queued", "pending", "running"]:
            break

        await edit_interaction(ctx, start_bot_message, message_update, file_update)

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


async def check_server_result_ok(result):
    if result.status_code != 200:
        error_message = result.content.decode("utf-8")
        error = f"_Server error: {error_message}_"
        return False, error
    return result.status_code == 200, None
