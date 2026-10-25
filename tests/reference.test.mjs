import test from 'node:test';
import assert from 'node:assert/strict';
import {compile,truth} from '../scripts/reference.mjs';
test('independent expression-tree interpreter verifies three distinct rewrites exhaustively',()=>{
 for(const[a,b]of[['Y X Y XOR C5 AND XOR','X C5 AND Y C10 AND OR'],['X Y AND X Y XOR OR','X Y OR'],['X Y SUB Y ADD','X']]){
  assert.deepEqual(truth(a),truth(b));assert(compile(b).cost<compile(a).cost);
 }
});
test('wraparound, logical shifts and subtraction order are unsigned nibble semantics',()=>{
 for(const[text,n]of[['C15 C1 ADD',0],['C0 C1 SUB',15],['C0 NOT',15],['C15 SHL1',14],['C15 SHR1',7]])assert(truth(text).every(v=>v===n));
});
test('different function or malformed program is never accepted as an equivalent rewrite',()=>{
 assert.notDeepEqual(truth('Y X Y XOR C5 AND XOR'),truth('X Y OR'));
 for(const text of ['X DUP','C16','X Y','X  Y ADD','X ADD'])assert.throws(()=>compile(text));
});
