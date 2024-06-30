from flask import request, jsonify
from runpod_sd_proxy import app, use_model, cur, logger
import requests
import os

RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY")
RUNPOD_BASE_URL = os.environ.get("RUNPOD_BASE_URL")
RUNPOD_BASE_URL_SDXL = os.environ.get("RUNPOD_BASE_URL_SDXL")
MODELS = []
TIMEOUT = os.environ.get("TIMEOUT", 120)
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
    if model not in [m["model_name"] for m in MODELS]:
        return jsonify({"error": "Invalid model"})
    cur.execute(f"UPDATE model SET use_model = '{model}' WHERE id = {use_model};")
    return jsonify({"sd_model_checkpoint": model})


@app.route("/sdapi/v1/txt2img", methods=["POST"])
def generate_image():
    """returns image"""
    request_body = request.json
    sd_request = {"input": request_body}
    headers = {"Authorization": f"Bearer {RUNPOD_API_KEY}"}
    model = cur.execute(
        f"SELECT use_model FROM model WHERE id = {use_model};"
    ).fetchone()[0]

    if model == "v1-5-sdxl" and RUNPOD_BASE_URL_SDXL is not None:
        logger.debug("using sdxl")
        del sd_request["input"]["batch_size"]
        del sd_request["input"]["steps"]
        sd_response = requests.post(
            RUNPOD_BASE_URL_SDXL,
            headers=headers,
            json=sd_request,
            timeout=TIMEOUT,
        )
        sd_response_json = sd_response.json()
        image = sd_response_json.get("output", {}).get("image_url", "")
        image = image.replace("data:image/png;base64,", "")
    elif model == "v1-5-pruned-emaonly":
        logger.debug("using pruned")
        sd_response = requests.post(
            RUNPOD_BASE_URL,
            headers=headers,
            json=sd_request,
            timeout=TIMEOUT,
        )
        sd_response_json = sd_response.json()
        image = sd_response_json.get("output", {}).get("images", [])[0]
    response = {"images": [image], "parameters": {}, "info": request_body.get("prompt")}
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9080, debug=True)
