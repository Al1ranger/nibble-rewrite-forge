import assert from 'node:assert/strict';
import {abi} from 'genlayer-js';
const id='a'.repeat(64),root='b'.repeat(64);
for(const[method,args]of[['get_machine',[]],['register',['demo','Y X Y XOR C5 AND XOR']],['get_job',[id]],['optimize',[id,root]],['get_artifact',[id]],['evaluate',[id,root,5,10]]]){
 const bytes=abi.calldata.encode(abi.calldata.makeCalldataObject(method,args,{}));assert.deepEqual(abi.calldata.encode(abi.calldata.decode(bytes)),bytes);
}console.log('6 SDK calldata roundtrips passed');
