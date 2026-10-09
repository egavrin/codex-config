# Cache vs network volume is a latency call, and the miss path looks like an idle queue

## Prompt

I'm deploying a 70B model from HuggingFace to a serverless endpoint and I'll be scaling
it across a few regions. Should I use the model cache or a network volume? Also, is the
cache available in every region?

## Expected behavior

The agent should do these actions:

1. Explain the choice in terms of **latency**. Neither a cache hit nor a miss causes download-time charges. Compared with a volume, the cache saves setup work, not money
2. Describe a cache miss correctly. Runpod delays worker startup until the model download completes. The **job stays in the queue**. The endpoint looks idle or blocked during the download
3. Prefer a **pre-loaded network volume** for a latency-sensitive endpoint at this size. State that the cache is a reasonable default when latency is not critical
4. Recommend **measurements of both options** with the user's model and region. Do not state a fixed threshold. Cache capacity uses a share of each host's disk, so capacity changes with the host. A measurement from another environment does not apply automatically
5. Note that a network volume is **pinned to one data center**, so multi-region means one
   pre-loaded volume per DC
6. For the region question, state that **Runpod publishes no list** of data centers with model-cache support. Offer the network-volume-capable DC list only as an explicitly marked approximation, or offer to deploy and measure

## Assertions

- Says download time is not billed, on hit or miss
- Describes the miss as a queued job / delayed worker start, not a billing leak
- Mentions the volume's single-data-center pinning for the multi-region case
- Suggests testing both rather than quoting a hard size cutoff
- Says capacity varies by host rather than implying a single platform-wide cache size
- Treats inconsistent cold starts across workers as expected, not as a broken endpoint
- Does not claim the worker bills while downloading
- Does not state a list of regions that support the model cache as fact
- Does not claim `--model-reference` makes cold starts fast unconditionally
