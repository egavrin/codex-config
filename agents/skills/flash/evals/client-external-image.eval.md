# Deploy a prebuilt vLLM image and call it over HTTP

## Prompt

I have a prebuilt Docker image `myorg/vllm-server:latest` that serves an
OpenAI-compatible API on an A100. Using runpod-flash, deploy it to a Runpod
serverless GPU endpoint and send a completion request to `/v1/completions`.

## Expected behavior

The agent should do these actions:

1. Create an `Endpoint` with `image="myorg/vllm-server:latest"` (client mode) plus `name=`, `gpu=GpuGroup.AMPERE_80`
2. Identify `image=` as client mode. It deploys the image and calls it through HTTP without a decorated function
3. Call the deployed endpoint with `await server.post("/v1/completions", {...})`

## Assertions

- Creates an `Endpoint(name=..., image="myorg/vllm-server:latest", gpu=GpuGroup.AMPERE_80, ...)`
- Does not wrap a Python function in a decorator (client mode, not decorator mode)
- Calls the endpoint with `await <ep>.post("/v1/completions", <payload>)`
- Uses `await` on the HTTP call
- Does not set `id=` together with `image=` (mutually exclusive)
