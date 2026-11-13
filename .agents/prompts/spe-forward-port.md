Current target is GCC14/SPE, not continued GCC8 consumer compatibility work.
Resume from docs/builds/gcc14-sdk-20261108/thunk-fix-20261112.md and docs/task.md.
Retain the successful C++ thunk fix; investigate the directed-rounding control
without suppressing tests. Qualify SDK/runtime packaging and clean roots before
resuming the distribution batch. Preserve earlier evidence and source caches.

Use $tabor-spe-forward-port. Compare the historical SPE compiler/runtime with the selected modern revision. Propose a bounded component patch, implement it when supported by the sources, and report ABI/runtime evidence separately from compilation. Keep the SDK integration contract explicit.
