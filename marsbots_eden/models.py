from dataclasses import dataclass
from dataclasses import field
from typing import List


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


@dataclass
class StableDiffusionConfig:
    text_input: str
    uc_text: str = "nsfw, poorly drawn face, ugly, tiling, out of frame, extra limbs, disfigured, deformed body, blurry, blurred, watermark, text, grainy, signature, cut off, draft"
    stream: bool = False
    stream_every: int = 1
    n_samples: int = 1
    width: int = 512
    height: int = 512
    init_image_data: str = None
    init_image_strength: float = 0.0
    init_image_inpaint_mode: str = "cv2_telea"
    mask_image_data: str = None
    mask_invert: bool = False
    interpolation_texts: List = field(default_factory=lambda: [])
    interpolation_seeds: List = field(default_factory=lambda: [])
    interpolation_init_images: List = field(default_factory=lambda: [])
    interpolation_init_images_use_img2txt: bool = False
    interpolation_init_images_top_k: int = 2
    interpolation_init_images_power: float = 3.0
    interpolation_init_images_min_strength: float = 0.2
    latent_smoothing_std: float = 0.1        
    scale_modulation: float = 0.1
    n_frames: int = 30
    loop: bool = False
    smooth: bool = False
    n_film: int = 0
    fps: int = 15
    sampler: str = "euler"
    steps: int = 60
    guidance_scale: float = 7.5
    seed: int = 13
    upscale_f: float = 1.0
    lora: str = "(none)"
    lora_scale: float = 0.8
    generator_name: str = "create"

