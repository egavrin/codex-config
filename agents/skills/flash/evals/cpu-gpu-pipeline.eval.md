# Build a CPU-preprocess then GPU-inference pipeline

## Prompt

Using runpod-flash, build a two-stage pipeline: a CPU stage that cleans raw data
with pandas, then a GPU stage that runs inference with torch. The CPU stage
should use a compute CPU instance and the GPU stage an A100. Wire them together.

## Expected behavior

The agent should do these actions:

1. Define a CPU `@Endpoint(cpu=CpuInstanceType.<type>, dependencies=["pandas"])` function
2. Define a GPU `@Endpoint(gpu=GpuGroup.AMPERE_80, dependencies=["torch"])` function
3. Import `pandas`/`torch` inside the respective functions
4. Chain them: `await infer(await preprocess(raw))`

## Assertions

- CPU stage uses `cpu=CpuInstanceType.<member>` and does not set `gpu=`
- GPU stage uses `gpu=GpuGroup.AMPERE_80` and does not set `cpu=`
- `pandas` listed in the CPU stage `dependencies`, `torch` in the GPU stage `dependencies`
- Places imports inside each decorated function
- Connects stages through `await`. The GPU call waits for the CPU result
- Does not put `gpu=` and `cpu=` on the same Endpoint
