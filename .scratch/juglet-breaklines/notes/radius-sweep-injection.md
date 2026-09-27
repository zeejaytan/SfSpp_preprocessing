Ticket 11: injecting the boundary-radius override into the headless extractor.

Two edits to edgeline_extraction_headless.cpp:

1. declare the hook (with a fallback declaration, so the file still compiles
   if the new .cpp is not linked into a given target);

2. after the adaptive radius is computed, let the env var override it.

Both are marked with SFS-T11 so they can be found and removed in one pass.
