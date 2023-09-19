from dataclasses import dataclass
from dataclasses import field
from typing import List, Optional


@dataclass
class SignInCredentials:
    apiKey: str
    apiSecret: str


@dataclass
class SourceSettings:
    author_id: int
    author_name: str
    guild_id: int
    guild_name: str
    channel_id: int
    channel_name: str
    origin: str = "discord"


# @dataclass
# class StableDiffusionConfig:
#     text_input: str
#     uc_text: Optional[str]
#     stream: Optional[bool]
#     stream_every: Optional[int]
#     n_samples: Optional[int]
#     width: Optional[int]
#     height: Optional[int]
#     init_image_data: Optional[str]
#     init_image_strength: Optional[float]
#     init_image_inpaint_mode: Optional[str]
#     mask_image_data: Optional[str]
#     mask_invert: Optional[bool]
#     interpolation_texts: Optional[List]
#     interpolation_seeds: Optional[List]
#     interpolation_init_images: Optional[List]
#     interpolation_init_images_use_img2txt: Optional[bool]
#     interpolation_init_images_top_k: Optional[int]
#     interpolation_init_images_power: Optional[float]
#     interpolation_init_images_min_strength: Optional[float]
#     latent_smoothing_std: Optional[float]
#     scale_modulation: Optional[float]
#     n_frames: Optional[int]
#     loop: Optional[bool]
#     smooth: Optional[bool]
#     n_film: Optional[int]
#     fps: Optional[int]
#     sampler: Optional[str]
#     steps: Optional[int]
#     guidance_scale: Optional[float]
#     seed: Optional[int]
#     upscale_f: Optional[float]
#     lora: Optional[str]
#     lora_scale: Optional[float]
#     generator_name: Optional[str]

@dataclass
class StableDiffusionConfig:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
