import fs from 'node:fs';
import {spawn} from 'node:child_process';
import assert from 'node:assert/strict';
import {getAddress} from 'viem';
import {rpc,receipt,source,read,digest,canonical} from './check.mjs';
import {checkArtifact,compile} from './reference.mjs';
const accounts=[{name:'studio-proof-deployer',address:getAddress('0x7a413bb4ab62e31d62d4cd9efc8c8a8dae37fb42')},
 {name:'fairresolve-demo',address:getAddress('0x34346773a22564cbcc5f1d67d1c1f9f196daea35')}];
const cases=[{name:'blend',program:'Y X Y XOR C5 AND XOR'},{name:'union',program:'X Y AND X Y XOR OR'},{name:'cancel',program:'X Y SUB Y ADD'}];
const file='PROOFS.json',commit=process.argv[2];assert(/^[0-9a-f]{40}$/.test(commit??''),'Supply published source commit');
let p=fs.existsSync(file)?JSON.parse(fs.readFileSync(file,'utf8')):{network:'studionet',chain_id:61999,source_commit:commit,accounts,cases,transactions:[],jobs:{},artifacts:{}};
assert.equal(p.source_commit,commit);const save=()=>fs.writeFileSync(file,JSON.stringify(p,null,2)+'\n');p.final_readback_verified=false;save();let phase='preflight';
function broadcast(args,account,onHash){return new Promise((resolve,reject)=>{
 const child=spawn(process.execPath,['scripts/run-cli.cjs',...args],{windowsHide:true,env:{...process.env,NRF_TEST_ACCOUNT:account.name},stdio:['ignore','pipe','pipe']});
 let carry='';child.stderr.resume();child.stdout.on('data',data=>{carry+=data.toString();const lines=carry.split(/\r?\n/);carry=lines.pop();
  for(const line of lines)if(/^BROADCAST_HASH 0x[0-9a-fA-F]{64}$/.test(line))onHash(line.split(' ')[1]);});
 child.on('error',()=>reject(Error('CLI launch failed')));child.on('close',resolve);
});}
async function tx(step,args,who=0,expected='SUCCESS',message){
 phase=step;let t=p.transactions.find(x=>x.step===step),account=accounts[who];
 if(!t){
  const latest=await rpc('eth_getTransactionCount',[account.address,'latest']),pending=await rpc('eth_getTransactionCount',[account.address,'pending']);assert.equal(latest,pending,'Pending signer transaction');
  t={step,signer:account.address,expected,cli_arguments:args,nonce_before:latest,verified:false,broadcast_unknown:true,...(message?{expected_message:message}:{})};p.transactions.push(t);save();
  t.cli_exit=await broadcast(args,account,hash=>{t.hash=hash;delete t.broadcast_unknown;save();console.log(step+' '+hash);});save();
 }
 assert.equal(t.signer,account.address);assert.equal(canonical(t.cli_arguments),canonical(args));if(!t.hash)throw Error('Unknown broadcast outcome: audit history before retry');
 Object.assign(t,await receipt(t.hash,expected,message),{verified:true});save();console.log(JSON.stringify({step,status:t.status,execution:t.execution,consensus:t.consensus}));
 if(expected==='SUCCESS'&&!t.committed)throw Error('No committed state');return t;
}
const write=(step,method,args,who=0,expected='SUCCESS',message)=>tx(step,['write',p.address,method,'--args',...args.map(String)],who,expected,message);
async function register(c){
 await write('register-'+c.name,'register',[c.name,c.program]);
 const id=digest({contract:p.address,owner:accounts[0].address,nonce:c.name}),job=await read(p.address,'get_job',[id]);
 assert.equal(job.job_id,id);assert.equal(job.program,c.program);assert.equal(job.source_cost,compile(c.program).cost);
 if(p.jobs[c.name])assert.equal(canonical(p.jobs[c.name]),canonical(job));p.jobs[c.name]=job;save();return job;
}
try{
 assert.equal(await rpc('eth_chainId',[]),'0xf22f');
 const deployed=await tx('deploy',['deploy','--contract','contracts/NibbleRewriteForge.py']);p.address=deployed.address;p.source=await source(p.address);p.machine=await read(p.address,'get_machine',[]);save();
 for(const c of cases){
  const job=await register(c);await write('optimize-'+c.name,'optimize',[job.job_id,job.input_root]);
  const artifact=await read(p.address,'get_artifact',[job.job_id]);checkArtifact(job,artifact,digest);
  if(p.artifacts[c.name])assert.equal(canonical(p.artifacts[c.name]),canonical(artifact));p.artifacts[c.name]=artifact;save();
  console.log(JSON.stringify({case:c.name,generated:artifact.program,source_cost:artifact.source_cost,cost:artifact.cost,checked:artifact.checked_inputs}));
 }
 const a=p.jobs.blend,b=p.jobs.union;
 await write('foreign-optimizer','optimize',[a.job_id,a.input_root],1,'ERROR','Only creator');
 await write('wrong-source-root','optimize',[b.job_id,'f'.repeat(64)],0,'ERROR','Input root mismatch');
 await write('registration-replay','register',['blend',cases[2].program],0,'ERROR','Nonce already used');
 await write('immutable-publication','optimize',[a.job_id,a.input_root],0,'ERROR','Artifact already published');
 await write('invalid-opcode','register',['invalid','X C16 ADD'],0,'ERROR','Invalid source program');
 const floor=await register({name:'floor',program:'X'});
 await write('positive-cost-floor','optimize',[floor.job_id,floor.input_root],0,'ERROR','No cheaper program under positive instruction costs');
 assert.equal(p.transactions.length,14);assert(p.transactions.every(t=>t.verified&&t.hash&&!t.broadcast_unknown));assert.equal(Object.keys(p.artifacts).length,3);
 p.workflow_complete=true;save();console.log(JSON.stringify({workflow_complete:true,address:p.address,transactions:14,artifacts:3}));
}catch(e){console.error('Workflow stopped at '+phase+' ('+(e instanceof assert.AssertionError?'assertion':'network/receipt check')+'); inspect journal before retry');process.exitCode=1;}
