// Read-only: no CLI, keys, generator, signing or send path.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {rpc,receipt,source,read,denied,digest,canonical} from './check.mjs';
import {checkArtifact,compile,truth,costs} from './reference.mjs';
const p=JSON.parse(fs.readFileSync('PROOFS.json','utf8'));
assert(p.workflow_complete);assert.equal(await rpc('eth_chainId',[]),'0xf22f');assert.equal(p.transactions.length,14);assert.equal(new Set(p.transactions.map(t=>t.hash)).size,14);
for(const t of p.transactions){
 assert(t.verified&&!t.broadcast_unknown);const r=await receipt(t.hash,t.expected,t.expected_message);assert.equal(r.address,p.address);assert.equal(r.committed,t.expected==='SUCCESS');
 const native=await rpc('eth_getTransactionByHash',[t.hash]);assert.equal(native.from_address.toLowerCase(),t.signer.toLowerCase());assert.equal(BigInt(native.nonce),BigInt(t.nonce_before));assert.equal(BigInt(native.value),0n);
}console.log('All fourteen receipts, native signers, nonces and zero values verified');
p.source=await source(p.address);const machine=await read(p.address,'get_machine',[]);
assert.deepEqual(machine,{policy:'nibble-rewrite-forge-v1',word_bits:4,inputs:['X','Y'],domain_size:256,costs,constant_cost:1,source_token_limit:40,rewrite_token_limit:24,stack_limit:16,cost_claim:'DECLARED_MODEL_ONLY_NOT_GAS_OR_GLOBAL_OPTIMALITY'});
assert.equal(canonical(machine),canonical(p.machine));p.native_evaluations=[];
for(const[name,job]of Object.entries(p.jobs)){
 assert.equal(canonical(await read(p.address,'get_job',[job.job_id])),canonical(job));assert.equal(job.owner,p.accounts[0].address);assert.equal(job.contract,p.address);assert.equal(job.nonce,name);
 assert.equal(job.job_id,digest({contract:p.address,owner:p.accounts[0].address,nonce:name}));assert.equal(job.machine_root,digest(machine));assert.equal(job.policy,machine.policy);
 assert.equal(job.input_root,digest(Object.fromEntries(Object.entries(job).filter(([k])=>k!=='input_root'))));assert.equal(job.source_cost,compile(job.program).cost);
 assert.equal(job.semantics_root,digest({policy:machine.policy,word_bits:4,order:'x-major-y-minor',values:truth(job.program)}));
 if(name==='floor'){assert.equal(job.program,'X');assert(await denied(p.address,'get_artifact',[job.job_id]));continue;}
 const artifact=await read(p.address,'get_artifact',[job.job_id]);assert.equal(canonical(artifact),canonical(p.artifacts[name]));checkArtifact(job,artifact,digest);
 for(const[x,y]of[[0,0],[15,15],[5,10],[15,1]]){
  const value=await read(p.address,'evaluate',[job.job_id,job.input_root,x,y]);
  assert.deepEqual(value,{value:compile(job.program).run(x,y),artifact_root:artifact.root,input_root:job.input_root,model_cost:artifact.cost});p.native_evaluations.push({case:name,x,y,...value});
 }
 assert(await denied(p.address,'evaluate',[job.job_id,'f'.repeat(64),0,0]));assert(await denied(p.address,'evaluate',[job.job_id,job.input_root,16,0]));
 console.log('Verified full 256-input equivalence, strict cost and reusable native evaluation: '+name);
}
assert.equal(Object.keys(p.jobs).length,4);assert.equal(Object.keys(p.artifacts).length,3);
const invalid=digest({contract:p.address,owner:p.accounts[0].address,nonce:'invalid'});assert(await denied(p.address,'get_job',[invalid]));
const history=await rpc('sim_getTransactionsForAddress',[p.address]);assert.deepEqual(history.map(t=>t.hash).sort(),p.transactions.map(t=>t.hash).sort());
p.contract_history_matched=true;p.final_readback_verified=true;fs.writeFileSync('PROOFS.json',JSON.stringify(p,null,2)+'\n');
console.log(JSON.stringify({verified:true,source:p.source,transactions:14,artifacts:3,formal_input_pairs_per_artifact:256,native_sample_evaluations:p.native_evaluations.length}));
