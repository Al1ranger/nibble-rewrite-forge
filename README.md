# NibbleRewriteForge

Experimental GenLayer **AI-synthesized, exhaustively checked cost-improving bitvector rewrites**. This is a formal computation primitive—not a graph transition, source oracle, service verifier, learned classifier, authorization certificate or proof of actual gas savings.

Users register an exact formal program. The leader must generate actual replacement code using `gl.nondet.exec_prompt`; callers cannot submit a candidate, equivalence label or cost. Validators independently execute the original and the leader's exact proposed artifact on **all 256 input pairs**, check the grammar/resource bounds and recompute strict abstract cost improvement before accepting publication.

## Boundary and consequential AI

`register(nonce, source_program)` → immutable creator-bound formal specification → creator invokes `optimize(job_id, input_root)` → AI searches for a rewrite → independent exhaustive verification → immutable executable artifact → anyone may repeatedly `evaluate(job_id, input_root, x, y)`.

The nondeterministic output is the executable program and its cost, not a decorative explanation. The contract contains **no rewrite-rule fallback, hardcoded demo optimizer, cached candidate or deterministic search that supplies the result**. A malformed, inequivalent or non-improving candidate does not publish an artifact. The register function and interpreter are ordinary deterministic components; the AI contribution is program synthesis.

No external observation is claimed. The complete input program is the specification itself, not a self-report of service delivery, knowledge accuracy or observed behavior. Consequently there are no observer URLs to leave unfetched. Validators receive and execute the full original program, not merely its hash. Hashes bind immutable context; they do not replace formal evaluation.

## Machine

- Two unsigned 4-bit inputs: X and Y, each 0–15. Every intermediate result is masked with 15.
- RPN stack grammar, single ASCII spaces: `X`, `Y`, `C0`…`C15`, unary `NOT`, `SHL1`, `SHR1`, and binary `AND`, `OR`, `XOR`, `ADD`, `SUB`.
- Binary operations pop b then a. `SUB` is `(a-b)&15`; `SHR1` is unsigned right shift. No memory, branches, division, jumps, DUP/SWAP, arbitrary Python or eval.
- Original: 1–40 tokens. Rewrite: 1–24 tokens. Both: at most 240 characters, maximum stack depth 16, exactly one final result.
- Loads/constants and NOT/AND/OR/shifts cost 1; XOR/ADD/SUB cost 2. Every instruction has positive cost.
- Publication requires **strictly lower total model cost** and exact output equality on every `(x,y)` in `{0,…,15}²`. No confidence, tolerance or sampled equivalence.

These are declared interpreter cost units, **not GenLayer gas, hardware cycles, energy or global optimality**. Finding one improved program does not prove it is the smallest possible program. Equivalence outside this 4-bit machine is not implied.

## Why validators do not generate a second candidate

Many different programs can be valid rewrites, with different costs. Requiring identical independent AI output would unnecessarily reject valid synthesis. The custom validator instead independently reconstructs the complete formal proof report for the **exact leader program** against the stored original specification. It executes the full finite domain and checks substantive equivalence, resource bounds and cost, not just JSON shape or a leader-provided claim. This is an objective, complete check within the bounded machine.

Every agreeing validator must verify that same artifact. Network finality is GenLayer majority consensus, not a promise of unanimous votes. After consensus, deterministic code repeats the proof checks before storage. A shared interpreter bug remains a risk; independent reference interpreters test the boundary.

## Storage and access

Two maps: immutable `jobs` and immutable `artifacts`, keyed by contract/native-creator/nonce. No central owner, mutable graph/head, certificate consume bit or token balances. Only the job creator can optimize; full input-root binding is mandatory. Publication is once per job, but **execution is reusable and permissionless**, not a one-time capability. The source cannot be replaced; a published artifact cannot be overwritten.

Invalid model output leaves the job pending. Retrying synthesis is allowed because every candidate must satisfy the same exact objective constraints; it cannot change the source function or accept a preferred subjective verdict. A one-cost source is rejected before model invocation because no positive-cost program can be cheaper. Other already-optimal programs may fail synthesis; liveness and globally optimal search are not guaranteed. No funds or credits are locked.

## Reproduce tests

```powershell
python -m pip install -r requirements-dev.txt
genvm-lint check contracts/NibbleRewriteForge.py --json
python -m pytest tests -q -p no:cacheprovider
npm ci --ignore-scripts
node --test tests/reference.test.mjs
node scripts/sdk-check.mjs
```

39 Python direct/helper/callback tests + 3 independent JavaScript tests; six SDK calldata roundtrips. The Python vector interpreter compares 1,645 generated expressions on all 256 inputs against the scalar production interpreter. JavaScript builds independent expression trees. A valid lower-cost candidate that differs **only at the final pair (15,15)** is rejected, demonstrating that sampling is insufficient. Actual callback tests reject a fully rehashed, shape-valid wrong-function artifact and forged cost/context, while accepting two syntactically distinct correct rewrites.

Direct tests do not establish live consensus. Their Windows fixture defers only gltest's open-temporary-file `WinError 32` cleanup; contract exceptions remain visible. Live results, if any, are published separately after source, receipts and artifact verification.

## Demo specifications

| Input program | Function | Example improved form (test-only, not a production fallback) |
|---|---|---|
| `Y X Y XOR C5 AND XOR` | Select X bits under mask 5, Y bits elsewhere | `X C5 AND Y C10 AND OR` |
| `X Y AND X Y XOR OR` | Bitwise union via disjoint AND/XOR components | `X Y OR` |
| `X Y SUB Y ADD` | Unsigned modular cancellation | `X` |

Live artifacts must come from the contract's AI call, not this table or the caller. Different equivalent lower-cost artifacts are acceptable; no hardcoded candidate is required by the proof scripts.

## Deployment discipline

StudioNet (61999) is gasless; use a dedicated native encrypted CLI test account and do not fund it or export its key. CLI 0.39.2 is used by owned proof tooling. `NRF_TEST_ACCOUNT` is a local account name; `NRF_CLI_PATH` overrides the sibling-workspace CLI fallback for a clean clone. `NRF_NATIVE_HTTP=1` enables Windows-native HTTPS only for the Studio API.

Proofs are submitted serially, with native nonce/intent journaled before sending and acknowledged hashes recorded immediately. The owned CLI child stops after acknowledgement; independent receipt checks determine execution success. If no hash is returned, stop and audit history/nonce before retrying. A known transaction is never blindly rebroadcast. Read-only verification has no signing/send path and checks native source, immutable roots, all 256 function values offline, and sampled native consumer calls. FINALIZED with ERROR is a rejection proof, not successful publication.

Generic encrypted-CLI transport, receipt inspection and Windows test cleanup are reused with attribution from [PeelSetManifests](https://github.com/Starling-spell/peelset-manifests) and its documented predecessors. The set-sketch architecture is not reused. [Architecture differences](docs/architecture.md), [security boundary](SECURITY.md).

Known superoptimization background: [Massalin, 1987](https://www.cse.iitm.ac.in/~krishna/courses/2022/odd-cs6013/MassalinCANews87.pdf). This does not claim to invent superoptimization or prove global novelty. Experimental, not production audited, no submission-acceptance guarantee, no automatic portal submission.
