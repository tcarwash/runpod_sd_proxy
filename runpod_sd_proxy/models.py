from pydantic import BaseModel
from typing import List, Optional


class SDOutputImages(BaseModel):
    images: List[str]
    info: Optional[str] = ""
    parameters: Optional[dict] = {}
    status: Optional[str] = ""


class SDOutput(BaseModel):
    output: SDOutputImages


class SDXLOutputImages(BaseModel):
    image_url: str
    images: List[Optional[str]] = []
    seed: Optional[int] = 0


class SDXLOutput(BaseModel):
    output: SDXLOutputImages


class SDRequestInput(BaseModel):
    prompt: str
    steps: Optional[int] = 20
    batch_size: Optional[int] = 1
    width: Optional[int] = 512
    height: Optional[int] = 512


class SDRequest(BaseModel):
    input: SDRequestInput


class SDXLRequestInput(BaseModel):
    prompt: str
    num_inference_steps: Optional[int] = 20
    num_images: Optional[int] = 1
    width: Optional[int] = 512
    height: Optional[int] = 512


class SDXLRequest(BaseModel):
    input: SDXLRequestInput
