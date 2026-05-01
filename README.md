## Anime4K Integration Experiment (ABANDONED)

This branch contains an incomplete integration of Anime4K CNN and GAN models.

- CNN: partially worked, but had ghosting; multiple shader fixes didn't restore correct upscaling.
- GAN: partially worked, had apparent binding issues which resulted in a fake upscaling (1x1 to 2x2 at pixel-level, not real GAN upscaling); feature maps never produced non-zero data and no fix was found to correct it.
- Possible root cause: the shader architecture (pixel shaders vs. compute, storage image bindings) was incompatible with our pipeline.
- Conclusion: not worth pursuing for our use case (window apps, games, visual novels).

**Kept for reference only. Do not merge.**
