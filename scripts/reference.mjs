import assert from 'node:assert/strict';
export const costs={X:1,Y:1,NOT:1,AND:1,OR:1,XOR:2,ADD:2,SUB:2,SHL1:1,SHR1:1};
export function compile(text,limit=40){
 assert.equal(typeof text,'string');assert(text.length>0&&text.length<=240);
 const tokens=text.split(' '),stack=[];let cost=0,peak=0;
 assert(tokens.length<=limit);
 for(const op of tokens){
  if(op==='X'||op==='Y'){stack.push((x,y)=>op==='X'?x:y);cost++;}
  else if(/^C(?:[0-9]|1[0-5])$/.test(op)){const n=Number(op.slice(1));stack.push(()=>n);cost++;}
  else if(['NOT','SHL1','SHR1'].includes(op)){
   assert(stack.length>=1);const a=stack.pop();stack.push((x,y)=>((op==='NOT'?~a(x,y):op==='SHL1'?a(x,y)*2:Math.floor(a(x,y)/2))&15));cost+=costs[op];
  }else{
   assert(['AND','OR','XOR','ADD','SUB'].includes(op));assert(stack.length>=2);const b=stack.pop(),a=stack.pop();
   stack.push((x,y)=>{const l=a(x,y),r=b(x,y);return (op==='AND'?l&r:op==='OR'?l|r:op==='XOR'?l^r:op==='ADD'?l+r:l-r)&15;});cost+=costs[op];
  }
  peak=Math.max(peak,stack.length);assert(peak<=16);
 }
 assert.equal(stack.length,1);return {run:stack[0],cost,peak,length:tokens.length};
}
export function truth(text,limit=40){const p=compile(text,limit);return Array.from({length:256},(_,i)=>p.run(i>>4,i&15));}
export function checkArtifact(job,artifact,digest){
 assert.deepEqual(artifact.spec,job);const before=compile(job.program),after=compile(artifact.program,24);
 assert(after.cost<before.cost);assert.deepEqual(truth(job.program),truth(artifact.program,24));
 const semantics=digest({policy:'nibble-rewrite-forge-v1',word_bits:4,order:'x-major-y-minor',values:truth(job.program)});
 assert.equal(job.source_cost,before.cost);assert.equal(job.semantics_root,semantics);assert.equal(artifact.semantics_root,semantics);
 assert.equal(artifact.cost,after.cost);assert.equal(artifact.source_cost,before.cost);assert.equal(artifact.saved_model_units,before.cost-after.cost);
 assert.equal(artifact.checked_inputs,256);assert.equal(artifact.instruction_count,after.length);assert.equal(artifact.peak_stack,after.peak);
 assert.equal(artifact.claim,'EXACT_4_BIT_EQUIVALENCE_AND_STRICT_DECLARED_COST_REDUCTION');
 assert.equal(artifact.root,digest(Object.fromEntries(Object.entries(artifact).filter(([k])=>k!=='root'))));return true;
}
