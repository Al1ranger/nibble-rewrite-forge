# Experimental security boundary

Not production audited. No funds, tokens, approvals, delegated arbitrary code, proxy upgrades, global admin or cross-contract writes. Nothing is economically locked by a pending or unsynthesizable job. Native encrypted test accounts sign gasless StudioNet transactions; never export keys or commit credentials.

- Register keys bind contract, native creator and nonce. Original formal program, declared machine, computed source cost and complete-domain semantics are immutable and root-bound.
- Only creator may optimize; caller must supply the exact original input root. Another principal cannot finalize the creator's job. A successful artifact is immutable and cannot be replaced by resampling.
- Model output is data in a strict whitelisted RPN grammar, never eval/exec/Python. No loops, memory, division, imports or user-defined opcodes. Max 40/24 source/rewrite tokens, 240 characters, stack depth 16, exactly one result. Unknown tokens, underflow and malformed/duplicate-key JSON are rejected.
- All values use exact unsigned 4-bit semantics and mask every intermediate. SUB pop order and logical shifts are explicit. All 256 input pairs are checked, not a sample or a probabilistic truth estimate.
- Cost is recomputed from actual instructions; every cost is positive. Non-improving, inequivalent or malformed candidates produce LLM_ERROR/disagreement/revert with no artifact. One-cost originals are deterministically rejected before invoking the generator.
- Validator checks substance against the complete source program and reconstructs the exact proof report, including context, cost, savings, complete-domain hash and program bounds. It does not trust leader claims, confidence, summaries or only JSON shape. Post-consensus checks repeat verification before writes.
- Root-bound evaluation is deliberately permissionless and repeatable. It is not a one-time capability or a certificate of authorization. Inputs outside 0–15, booleans and wrong roots are rejected.
- Shared interpreter bugs remain a risk. Independent vector/expression-tree interpreters, exhaustive expression comparisons, final-input-only mismatch tests and actual callback forgeries test this boundary. Direct mocks do not establish live consensus.
- Optimization is not guaranteed to terminate or find an improvement. A failed model may be retried under the same immutable objective; no subjective verdict is resampled. No global minimum, real gas reduction, external-world correctness, delivery or authority guarantee.

Solidity analyzers do not apply to this Python GenVM source. Pre-deploy evidence requires GenVM lint/SDK validation, direct/helper/callback tests, independent reference tests, SDK roundtrips and separately verified live receipts/source. Reused generic test/transport helpers retain upstream MIT notices.
