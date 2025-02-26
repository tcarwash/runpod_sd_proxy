a basic flask proxy that converts stable diffusion api's txt2img or equivalent SDXL endpoint to work with runpod serverless stable diffusion containers ("SD Automatic1111" or "Stable Diffusion XL" quick deploy templates). It implements or spoofs ONLY the endpoints required to work with open-webui for image generation.

1. create `.env` file based on `env_example`
2. `docker compose build` or `docker compose pull`
3. `docker compose up`

this image is intended to be added to the open-webui docker-compose file to run alongside that project.

NO AUTHENTICATION is implemented at this time, this is purely intended for open-webui to talk to it.

An example docker-compose.yml file where this container is added to the standard open-webui compose file:

```yaml
services:
  open-webui: --
  -- standard open-webui compose here...
  sd-proxy:
    image: ghcr.io/tcarwash/runpod_sd_proxy:latest
    ports:
      - 9080:9080
    environment:
      - "RUNPOD_API_KEY=YOUR_RUNPOD_APIKEY"
      - "RUNPOD_BASE_URL=https://api.runpod.ai/v2/YOUR_RUNPOD_INSTANCE/runsync"
      -- see env_example for available options
    restart: unless-stopped
    links:
      - open-webui
```
