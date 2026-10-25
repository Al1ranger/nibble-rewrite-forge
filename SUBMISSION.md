# Ready-to-fill submission

Contribution type: **Builder → Intelligent Contracts**

## Title

NibbleRewriteForge — AI Rewrites with Exhaustive Equivalence

## Notes / Description

NibbleRewriteForge publishes lower-cost AI-generated 4-bit programs. A creator registers an immutable RPN source. The contract invokes an LLM to synthesize replacement code; callers cannot supply the candidate or an equivalence verdict.

Validators independently execute the original and exact proposed rewrite on all 256 input pairs, validate stack/opcode bounds, and recompute strict improvement under a declared instruction-cost model. Invalid, inequivalent or non-improving candidates cannot publish. Different valid code spellings are allowed; no second AI candidate is required for a complete formal check.

Published artifacts support repeated, permissionless, original-root-bound evaluation. Creator authorization, immutable input roots and nonce bindings prevent substitution and overwrite. Live proofs cover three synthesized rewrites and rejected unauthorized/replayed calls. This is formal computation, not an oracle, certificate, proof of real-world delivery or measured gas savings.

996/1000 characters.

## Evidence

- [Repository](https://github.com/Al1ranger/nibble-rewrite-forge)
- [Contract source](https://github.com/Al1ranger/nibble-rewrite-forge/blob/main/contracts/NibbleRewriteForge.py)
- [Architecture and differences](https://github.com/Al1ranger/nibble-rewrite-forge/blob/main/docs/architecture.md)
- [Actual generated code and fourteen-receipt matrix](https://github.com/Al1ranger/nibble-rewrite-forge/blob/main/LIVE_PROOFS.md)
- [Machine-readable ledger](https://github.com/Al1ranger/nibble-rewrite-forge/blob/main/PROOFS.json)
- [Explorer contract](https://explorer-studio.genlayer.com/address/0xd2cC2EAB289B45CCfabb8ac5419c271b631DA3bb)
- [deploy](https://explorer-studio.genlayer.com/tx/0xb931663ed8488cd8946488b4da544b8fe00f6f671df5fd60502c2cbb74be73bd)
- [optimize-blend](https://explorer-studio.genlayer.com/tx/0xbc5c277f0179a33f2427808ddb119ddf638dc2014b7c755b160beb5c2cb092d6)
- [optimize-union](https://explorer-studio.genlayer.com/tx/0x719a8f77c2401a9f6eeacdb5dd2dd20084b8ef711a4ff360a2ad0c3f3908a6fa)
- [optimize-cancel](https://explorer-studio.genlayer.com/tx/0x91041188f5f6b2602a62d9b256d53a192693fda02a2f99b37d696fcc6bb778f6)
- [foreign-optimizer](https://explorer-studio.genlayer.com/tx/0x16d413d20c5a2fc917d99b23b5b5353b71b9d34370b65cd37fd478df0eb19912)
- [wrong-source-root](https://explorer-studio.genlayer.com/tx/0x2484ad775206462f53ee243199a20b879282d19b8822b075643b694982b1b5f1)
- [registration-replay](https://explorer-studio.genlayer.com/tx/0x187ebd5db50c6ed0c5bd84321fa35d6328ddb1b84afe8e50929c8feb7aaa9e1e)
- [immutable-publication](https://explorer-studio.genlayer.com/tx/0x69bfa8b3a4b2d1d96df717ba8d6bb195b10a687442042ccd47a0b2737fcb4b39)
- [positive-cost-floor](https://explorer-studio.genlayer.com/tx/0xf418c30b54b4626abde644f3c45e07cbd05f76c11e8088b1b7b965911960ef31)

## Optional steward response

Implemented an AI program-synthesis primitive, not another versioned graph or renamed evidence certificate. The nondeterministic output is executable replacement code with strictly lower declared cost. Each validator independently checks the exact artifact against the complete original program over the entire 4-bit input domain; JSON shape, source hashes or confidence do not substitute for equivalence. Matching repository/deployed source, actual generated programs, exhaustive checks and positive/negative receipts are linked.

## Scope

Experimental, not production audited. 8 successful and 6 expected-error finalized transactions. Complete equivalence is only for this bounded machine; no wider-word, external-reality, actual-gas or global-optimum guarantee. No automatic portal submission and no claim that superoptimization itself is new.
