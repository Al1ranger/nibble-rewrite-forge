# Live proofs — NibbleRewriteForge

Experimental formal computation on StudioNet, chain 61999. No external-world observation, actual gas, inventory or delivery claim.

[Explorer source](https://explorer-studio.genlayer.com/address/0xd2cC2EAB289B45CCfabb8ac5419c271b631DA3bb) · [Repository source](https://github.com/Al1ranger/nibble-rewrite-forge/blob/main/contracts/NibbleRewriteForge.py) · [Machine-readable proof ledger](https://github.com/Al1ranger/nibble-rewrite-forge/blob/main/PROOFS.json)

- Contract: `0xd2cC2EAB289B45CCfabb8ac5419c271b631DA3bb`
- Normalized deployed source SHA-256: `b3b5634b762c6c81ecbabafd42dd95a2a293d0260e8676647b01b6de0d944698`
- Published original source commit: [70e36ec731386fdda9409b34d94f23b079c2738b](https://github.com/Al1ranger/nibble-rewrite-forge/tree/70e36ec731386fdda9409b34d94f23b079c2738b)
- 14 finalized transactions: 8 execution successes, 6 expected execution errors; all MAJORITY_AGREE, leader-only false, at least 5 initial validators and 3 explicit agree votes. Idle/dissent votes remain visible. This is not a unanimity claim.
- Source, native sender/nonce/zero-value bindings, exact transaction history, four immutable specifications and three AI artifacts independently checked read-only.

## Actual AI-generated artifacts

| Case | Original program | Generated program | Declared model cost | Formal pairs checked |
|---|---|---|---|---|
| blend | `Y X Y XOR C5 AND XOR` | `X C5 AND Y C10 AND OR` | 9 → 7 (2 saved) | 256 |
| union | `X Y AND X Y XOR OR` | `X Y OR` | 8 → 3 (5 saved) | 256 |
| cancel | `X Y SUB Y ADD` | `X` | 7 → 1 (6 saved) | 256 |

The generated programs above are read from onchain artifacts. The caller/proof script supplied only originals, not candidates. No example rewrite was substituted after a failure. Each agreeing validator independently checked the exact proposed artifact on **all 256** input pairs before publication. The read-only checker re-derived equivalence again using an independent expression-tree interpreter. These are abstract instruction-cost reductions, **not measured gas savings or proven global optima**.

## Transaction matrix

| Transaction | Finality / execution | Verified effect or error | Votes |
|---|---|---|---|
| [deploy](https://explorer-studio.genlayer.com/tx/0xb931663ed8488cd8946488b4da544b8fe00f6f671df5fd60502c2cbb74be73bd) | FINALIZED / SUCCESS | Contract deployed | 3 agree, 2 idle, 0 disagree |
| [register-blend](https://explorer-studio.genlayer.com/tx/0x054f2759314d366eedb1ab068753d91e8141fafaec8419093dcf46e6ff27301f) | FINALIZED / SUCCESS | Immutable formal input registered | 5 agree, 0 idle, 0 disagree |
| [optimize-blend](https://explorer-studio.genlayer.com/tx/0xbc5c277f0179a33f2427808ddb119ddf638dc2014b7c755b160beb5c2cb092d6) | FINALIZED / SUCCESS | AI-generated artifact published | 3 agree, 2 idle, 0 disagree |
| [register-union](https://explorer-studio.genlayer.com/tx/0x325f0a57508c2f0c58608110d9216c3438f0470f9ccc8c2bbd179fd316e53285) | FINALIZED / SUCCESS | Immutable formal input registered | 3 agree, 2 idle, 0 disagree |
| [optimize-union](https://explorer-studio.genlayer.com/tx/0x719a8f77c2401a9f6eeacdb5dd2dd20084b8ef711a4ff360a2ad0c3f3908a6fa) | FINALIZED / SUCCESS | AI-generated artifact published | 3 agree, 2 idle, 0 disagree |
| [register-cancel](https://explorer-studio.genlayer.com/tx/0xc182c9402b146900035cd56d12de2de16d201b9e2a9f356c09ecd2d0a3c9595f) | FINALIZED / SUCCESS | Immutable formal input registered | 3 agree, 2 idle, 0 disagree |
| [optimize-cancel](https://explorer-studio.genlayer.com/tx/0x91041188f5f6b2602a62d9b256d53a192693fda02a2f99b37d696fcc6bb778f6) | FINALIZED / SUCCESS | AI-generated artifact published | 3 agree, 2 idle, 0 disagree |
| [foreign-optimizer](https://explorer-studio.genlayer.com/tx/0x16d413d20c5a2fc917d99b23b5b5353b71b9d34370b65cd37fd478df0eb19912) | FINALIZED / ERROR | Only creator | 5 agree, 0 idle, 0 disagree |
| [wrong-source-root](https://explorer-studio.genlayer.com/tx/0x2484ad775206462f53ee243199a20b879282d19b8822b075643b694982b1b5f1) | FINALIZED / ERROR | Input root mismatch | 3 agree, 2 idle, 0 disagree |
| [registration-replay](https://explorer-studio.genlayer.com/tx/0x187ebd5db50c6ed0c5bd84321fa35d6328ddb1b84afe8e50929c8feb7aaa9e1e) | FINALIZED / ERROR | Nonce already used | 5 agree, 0 idle, 0 disagree |
| [immutable-publication](https://explorer-studio.genlayer.com/tx/0x69bfa8b3a4b2d1d96df717ba8d6bb195b10a687442042ccd47a0b2737fcb4b39) | FINALIZED / ERROR | Artifact already published | 3 agree, 2 idle, 0 disagree |
| [invalid-opcode](https://explorer-studio.genlayer.com/tx/0x60895e5e476c083beda08ea7525f65f72f821e66d84d49d24cb8e61400f462c6) | FINALIZED / ERROR | Invalid source program | 3 agree, 2 idle, 0 disagree |
| [register-floor](https://explorer-studio.genlayer.com/tx/0x94b87ddb14b4e363cfdb73d7a04bfd4c13231a9a47b4edca83c5d5be197d890d) | FINALIZED / SUCCESS | Immutable formal input registered | 3 agree, 2 idle, 0 disagree |
| [positive-cost-floor](https://explorer-studio.genlayer.com/tx/0xf418c30b54b4626abde644f3c45e07cbd05f76c11e8088b1b7b965911960ef31) | FINALIZED / ERROR | No cheaper program under positive instruction costs | 3 agree, 2 idle, 0 disagree |

## Consumer and binding evidence

- 12 sampled native read evaluations (four pairs per artifact) match the original functions, return the bound original input root and exact immutable artifact root. Full 256-case equivalence is performed inside the contract at publication and independently rechecked offline; this is not a claim that 256 separate native read transactions were sent.
- Wrong original roots and out-of-domain inputs revert. A floor-cost source has no artifact. The malformed source registration created no job.
- A peer cannot finalize another creator's job. Replaying a nonce with a different original cannot replace the source. Re-optimizing a published job cannot overwrite the artifact.
- All fourteen hashes exactly match contract transaction history; no hidden retries or duplicate deployment is cited. A finalized ERROR is a rejection proof, not successful publication.

## Local evidence, not additional onchain claims

39 Python direct/helper/callback + 3 independent JavaScript tests; six SDK roundtrips; GenVM lint and SDK validation pass. An independent vector interpreter checks 1,645 generated expressions across all 256 inputs. A valid cheaper program differing only at (15,15) is rejected. The actual callback rejects a fully rehashed shape-valid wrong-function report, fake cost and substituted creator context, and accepts two distinct valid program spellings. Direct mode alone does not establish live consensus.

Read-only verification: `node --require ./scripts/native-http.cjs scripts/verify-live.mjs`. Re-render only after verification: `node scripts/render-proofs.mjs`. No key or wallet is needed by either verifier.
