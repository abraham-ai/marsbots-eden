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


@dataclass
class EdenClipXConfig:
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
    num_iterations: tuple[int] = (100, 200, 300)
    octave_scale: float = 2.0
    clip_model_options: List = field(
        default_factory=lambda: [["ViT-B/32", "ViT-B/16", "RN50"]],
    )
    generator_name: str = "eden-clipx"


@dataclass
class StableDiffusionConfig:
    mode: str
    text_input: str
    uc_text: str = ""
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
    n_frames: int = 30
    loop: bool = False
    smooth: bool = False
    n_film: int = 0
    fps: int = 12
    sampler: str = "klms"
    steps: int = 50
    scale: float = 12.5
    seed: int = 13
    upscale_f: float = 1.0
    generator_name: str = "stable-diffusion"


@dataclass
class DreamBoothBannyConfig:
    prompt: str
    seed: int
    width: int = 512
    height: int = 512
    num_outputs: int = 1
    num_inference_steps: int = 50
    guidance_scale: float = 8.0
    generator_name: str = "dreambooth-banny"



@dataclass
class OracleConfig:
    text_input: str
    generator_name: str = "oracle"
