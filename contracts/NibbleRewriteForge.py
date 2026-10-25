# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
import hashlib
import json
import re
from genlayer import *

POLICY = "nibble-rewrite-forge-v1"
COSTS = {"X": 1, "Y": 1, "NOT": 1, "AND": 1, "OR": 1, "XOR": 2,
         "ADD": 2, "SUB": 2, "SHL1": 1, "SHR1": 1}
UNARY = ("NOT", "SHL1", "SHR1")
BINARY = ("AND", "OR", "XOR", "ADD", "SUB")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def fail(message):
    raise gl.vm.UserError("[EXPECTED] " + message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def program(text, limit):
    if not isinstance(text, str) or not 1 <= len(text) <= 240:
        raise ValueError("Program size")
    tokens = text.split(" ")
    if not 1 <= len(tokens) <= limit or text != " ".join(tokens):
        raise ValueError("Token bound")
    depth, peak, cost = 0, 0, 0
    for token in tokens:
        constant = re.fullmatch(r"C(?:[0-9]|1[0-5])", token) is not None
        if token in ("X", "Y") or constant:
            depth += 1
            cost += 1
        elif token in UNARY:
            if depth < 1:
                raise ValueError("Unary underflow")
            cost += COSTS[token]
        elif token in BINARY:
            if depth < 2:
                raise ValueError("Binary underflow")
            depth -= 1
            cost += COSTS[token]
        else:
            raise ValueError("Unknown token")
        peak = max(peak, depth)
        if peak > 16:
            raise ValueError("Stack bound")
    if depth != 1:
        raise ValueError("Exactly one result required")
    return {"tokens": tokens, "cost": cost, "length": len(tokens), "peak": peak}


def execute(tokens, x, y):
    stack = []
    for token in tokens:
        if token == "X":
            stack.append(x)
        elif token == "Y":
            stack.append(y)
        elif token.startswith("C"):
            stack.append(int(token[1:]))
        elif token in UNARY:
            a = stack.pop()
            stack.append(((~a) if token == "NOT" else (a << 1) if token == "SHL1" else (a >> 1)) & 15)
        else:
            b, a = stack.pop(), stack.pop()
            value = (a & b) if token == "AND" else (a | b) if token == "OR" else (a ^ b) if token == "XOR" else (a + b) if token == "ADD" else (a - b)
            stack.append(value & 15)
    return stack[0]


def table(tokens):
    return [execute(tokens, x, y) for x in range(16) for y in range(16)]


def semantics_root(values):
    return digest({"policy": POLICY, "word_bits": 4, "order": "x-major-y-minor", "values": values})


def candidate(raw):
    if isinstance(raw, str):
        raw = json.loads(raw, object_pairs_hook=unique_pairs)
    if not isinstance(raw, dict) or set(raw) != {"program"} or not isinstance(raw["program"], str):
        raise ValueError("Expected program-only JSON")
    return raw["program"]


def prove(spec, proposed):
    original, rewrite = program(spec["program"], 40), program(proposed, 24)
    if rewrite["cost"] >= original["cost"]:
        raise ValueError("No strict model-cost improvement")
    old_values, new_values = table(original["tokens"]), table(rewrite["tokens"])
    if old_values != new_values:
        raise ValueError("Not equivalent over all 256 inputs")
    if semantics_root(old_values) != spec["semantics_root"] or original["cost"] != spec["source_cost"]:
        raise ValueError("Source specification mismatch")
    proof = {"spec": spec, "program": proposed, "cost": rewrite["cost"], "source_cost": original["cost"],
             "saved_model_units": original["cost"] - rewrite["cost"], "checked_inputs": 256,
             "semantics_root": semantics_root(new_values), "instruction_count": rewrite["length"],
             "peak_stack": rewrite["peak"], "claim": "EXACT_4_BIT_EQUIVALENCE_AND_STRICT_DECLARED_COST_REDUCTION"}
    proof["root"] = digest(proof)
    return proof


def prompt(spec):
    return ("NIBBLE_REWRITE_V1. Synthesize a STRICTLY LOWER-COST equivalent stack program. "
            "Return only JSON with exactly one string key: program. No prose or extra fields. "
            "There are exactly two inputs X,Y, each integer 0..15. ALL intermediate values are masked with 15. "
            "RPN tokens separated by single ASCII spaces: X Y C0..C15 push a value. Unary NOT computes (~a)&15; "
            "SHL1 computes (a<<1)&15; SHR1 computes a>>1. Binary operations pop b then a: AND a&b, OR a|b, "
            "XOR a^b, ADD (a+b)&15, SUB (a-b)&15. Exactly one stack result must remain. "
            "No DUP, SWAP, eval, Python, shift constants, branches or other instructions. Maximum 24 tokens, "
            "maximum stack depth 16. Each load/constant costs 1; opcode costs are given below. "
            "Your total cost must be STRICTLY less than source_cost, and output identical for EVERY one of the "
            "256 input pairs, not just examples. Find algebraic identities, redundant work, mask simplifications "
            "or alternative Boolean/arithmetic constructions. This is a declared abstract cost, NOT gas or hardware timing. "
            "Do not copy the original if it is not cheaper. Do not merely claim equivalence. Actual code is required. "
            "COSTS=" + canonical(COSTS) + " SOURCE_PROGRAM=" + canonical(spec["program"]) + " SOURCE_COST=" + str(spec["source_cost"]))


def synthesize(spec):
    def leader():
        try:
            proposed = candidate(gl.nondet.exec_prompt(prompt(spec), response_format="json"))
            return prove(spec, proposed)
        except Exception:
            raise gl.vm.UserError("[LLM_ERROR] Invalid, non-equivalent or non-improving rewrite")

    def validator(result):
        if not isinstance(result, gl.vm.Return):
            return False
        try:
            if not isinstance(result.calldata, dict) or not isinstance(result.calldata.get("program"), str):
                return False
            # No second candidate is needed: independently execute the source AND
            # the leader's exact artifact over the complete formal input domain.
            checked = prove(spec, result.calldata["program"])
            return canonical(result.calldata) == canonical(checked)
        except Exception:
            return False

    proof = gl.vm.run_nondet_unsafe(leader, validator)
    try:
        if canonical(proof) != canonical(prove(spec, proof["program"])):
            raise ValueError("Invalid proof report")
    except Exception:
        raise gl.vm.UserError("[LLM_ERROR] Invalid consensus rewrite")
    return proof


class NibbleRewriteForge(gl.Contract):
    jobs: TreeMap[str, str]
    artifacts: TreeMap[str, str]

    def __init__(self):
        pass

    @gl.public.view
    def get_machine(self) -> dict:
        return {"policy": POLICY, "word_bits": 4, "inputs": ["X", "Y"], "domain_size": 256,
                "costs": COSTS, "constant_cost": 1, "source_token_limit": 40, "rewrite_token_limit": 24,
                "stack_limit": 16, "cost_claim": "DECLARED_MODEL_ONLY_NOT_GAS_OR_GLOBAL_OPTIMALITY"}

    @gl.public.write
    def register(self, nonce: str, source_program: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,48}", nonce):
            fail("Invalid nonce")
        contract, owner = str(gl.message.contract_address), str(gl.message.sender_address)
        key = digest({"contract": contract, "owner": owner, "nonce": nonce})
        if key in self.jobs:
            fail("Nonce already used")
        try:
            parsed = program(source_program, 40)
        except Exception:
            fail("Invalid source program")
        spec = {"contract": contract, "owner": owner, "nonce": nonce, "job_id": key, "policy": POLICY,
                "machine_root": digest(self.get_machine()), "program": source_program, "source_cost": parsed["cost"],
                "semantics_root": semantics_root(table(parsed["tokens"]))}
        spec["input_root"] = digest(spec)
        self.jobs[key] = canonical(spec)
        return key

    @gl.public.view
    def get_job(self, job_id: str) -> dict:
        if job_id not in self.jobs:
            fail("Unknown job")
        return json.loads(self.jobs[job_id])

    @gl.public.write
    def optimize(self, job_id: str, expected_input_root: str) -> str:
        spec = self.get_job(job_id)
        if str(gl.message.sender_address) != spec["owner"]:
            fail("Only creator")
        if expected_input_root != spec["input_root"]:
            fail("Input root mismatch")
        if job_id in self.artifacts:
            fail("Artifact already published")
        if spec["source_cost"] <= 1:
            fail("No cheaper program under positive instruction costs")
        proof = synthesize(spec)
        if self.jobs[job_id] != canonical(spec) or job_id in self.artifacts:
            fail("Job context changed")
        self.artifacts[job_id] = canonical(proof)
        return proof["root"]

    @gl.public.view
    def get_artifact(self, job_id: str) -> dict:
        if job_id not in self.artifacts:
            fail("No published artifact")
        return json.loads(self.artifacts[job_id])

    @gl.public.view
    def evaluate(self, job_id: str, expected_input_root: str, x: int, y: int) -> dict:
        spec = self.get_job(job_id)
        if expected_input_root != spec["input_root"]:
            fail("Input root mismatch")
        if type(x) is not int or type(y) is not int or not 0 <= x < 16 or not 0 <= y < 16:
            fail("Inputs must be integers 0 through 15")
        artifact = self.get_artifact(job_id)
        return {"value": execute(program(artifact["program"], 24)["tokens"], x, y), "artifact_root": artifact["root"],
                "input_root": spec["input_root"], "model_cost": artifact["cost"]}
