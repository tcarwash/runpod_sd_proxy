from flask import request, jsonify
from runpod_sd_proxy import app, use_model, cur, logger, db
from runpod_sd_proxy.models import (
    SDOutput,
    SDXLOutput,
    SDRequest,
    SDXLRequest,
    SDRequestInput,
    SDXLRequestInput,
)
import requests
import os
import json
from pydantic import ValidationError

RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY")
RUNPOD_BASE_URL = os.environ.get("RUNPOD_BASE_URL")
RUNPOD_BASE_URL_SDXL = os.environ.get("RUNPOD_BASE_URL_SDXL")
SD_OVERRIDES = json.loads(os.environ.get("SD_OVERRIDES", "{}"))
SDXL_OVERRIDES = json.loads(os.environ.get("SDXL_OVERRIDES", "{}"))
MODELS = []
TIMEOUT = int(os.environ.get("TIMEOUT", 120))
if RUNPOD_BASE_URL is not None:
    MODELS = [
        {
            "title": "v1-5",
            "model_name": "v1-5-pruned-emaonly",
        }
    ]
if RUNPOD_BASE_URL_SDXL is not None:
    MODELS.append(
        {
            "title": "v1-5-sdxl",
            "model_name": "v1-5-sdxl",
        }
    )

if not MODELS:
    raise ValueError(
        "No models available, you must specify RUNPOD_API_KEY and at least one of RUNPOD_BASE_URL or RUNPOD_BASE_URL_SDXL"
    )


@app.route("/sdapi/v1/sd-models")
def models():
    """returns models"""
    logger.debug(MODELS)
    return jsonify(MODELS)


@app.route("/sdapi/v1/options")
def options():
    """returns model options"""
    model = cur.execute(
        f"SELECT use_model FROM model WHERE id = {use_model};"
    ).fetchone()[0]
    logger.debug(model)
    return jsonify({"sd_model_checkpoint": model})


@app.route("/sdapi/v1/options", methods=["POST"])
def options_post():
    """returns image"""
    model = request.json.get("sd_model_checkpoint")
    logger.debug("requested model: " + model)
    if model not in [m["title"] for m in MODELS]:
        logger.debug("Invalid model requested")
        return jsonify({"error": "Invalid model"})
    model = next(m["model_name"] for m in MODELS if m["title"] == model)
    cur.execute(f"UPDATE model SET use_model = '{model}' WHERE id = {use_model};")
    db.commit()
    return jsonify({"sd_model_checkpoint": model})


def pruned_sd_request(sd_request: SDRequest, headers):
    sd_request.input.__dict__.update(SD_OVERRIDES)
    logger.debug("using pruned")
    logger.debug(f"sending: {sd_request.model_dump()}")
    response = requests.post(
        RUNPOD_BASE_URL,
        headers=headers,
        json=sd_request.model_dump(),
        timeout=TIMEOUT,
    )
    response = SDOutput.model_validate(response.json())
    image = response.output.images[0]

    return image


def sdxl_sd_request(sd_request: SDRequest, headers):
    logger.debug("using sdxl")
    sdxl_request = SDXLRequest(
        input=SDXLRequestInput(
            prompt=sd_request.input.prompt,
            num_inferenece_steps=sd_request.input.steps,
            num_images=sd_request.input.batch_size,
            width=sd_request.input.width,
            height=sd_request.input.height,
        )
    )
    sdxl_request.input.__dict__.update(SDXL_OVERRIDES)
    logger.debug(f"sending: {sdxl_request.model_dump()}")
    response = requests.post(
        RUNPOD_BASE_URL_SDXL,
        headers=headers,
        json=sdxl_request.model_dump(),
        timeout=TIMEOUT,
    )
    sd_response = SDXLOutput.model_validate(response.json())
    image = sd_response.output.image_url
    image = image.replace("data:image/png;base64,", "")

    return image


model_method_map = {
    "v1-5-pruned-emaonly": {"method": pruned_sd_request},
    "v1-5-sdxl": {"method": sdxl_sd_request},
}


def generate_image_based_on_model(method, request_body: SDRequest):
    logger.debug(request_body.model_dump())
    headers = {"Authorization": f"Bearer {RUNPOD_API_KEY}"}
    image = method(request_body, headers)

    return image


@app.route("/sdapi/v1/txt2img", methods=["POST"])
def generate_image():
    """returns image"""
    logger.debug(request.json)
    request_body = SDRequest.model_validate({"input": request.json})

    model = cur.execute(
        f"SELECT use_model FROM model WHERE id = {use_model};"
    ).fetchone()[0]

    if model == "v1-5-sdxl" and RUNPOD_BASE_URL_SDXL is None:
        return jsonify({"error": "No sdxl endpoint provided: set RUNPOD_BASE_URL_SDXL"})
    elif model == "v1-5-pruned-emaonly" and RUNPOD_BASE_URL is None:
        return jsonify({"error": "No pruned endpoint provided: set RUNPOD_BASE_URL"})

    try:
        model_method = model_method_map.get(model).get("method")
    except ValueError("Invalid model"):
        return jsonify({"error": "Invalid model"})

    logger.debug(request_body.model_dump())

    image = generate_image_based_on_model(model_method, request_body)

    response = {
        "images": [image],
        "parameters": {},
        "info": request_body.model_dump().get("prompt"),
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9080, debug=True)
