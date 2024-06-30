from flask import Flask, request, jsonify
import requests
import os

RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY")
RUNPOD_BASE_URL = os.environ.get("RUNPOD_BASE_URL")

app = Flask(__name__)


@app.route("/sdapi/v1/sd-models")
def models():
    """returns models"""
    response = [
        {
            "title": "v1-5",
            "model_name": "v1-5-pruned-emaonly",
        }
    ]
    return jsonify(response)


@app.route("/sdapi/v1/options")
def options():
    """returns model options"""
    return jsonify({"sd_model_checkpoint": "v1-5-pruned-emaonly"})


@app.route("/sdapi/v1/options", methods=["POST"])
def options_post():
    """returns image"""
    model = request.json.get("sd_model_checkpoint")
    return jsonify({"sd_model_checkpoint": model})


@app.route("/sdapi/v1/txt2img", methods=["POST"])
def generate_image():
    """returns image"""
    prompt = request.json.get("prompt")
    sd_request = {"input": {"prompt": prompt}}

    headers = {"Authorization": f"Bearer {RUNPOD_API_KEY}"}

    sd_response = requests.post(
        RUNPOD_BASE_URL,
        headers=headers,
        json=sd_request,
    )
    sd_response_json = sd_response.json()
    image = sd_response_json.get("output", {}).get("images", [])[0]
    response = {"images": [image], "parameters": {}, "info": prompt}
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9080, debug=True)
