import ast
import copy
import hashlib
import itertools
import json
import operator
import re
from pathlib import Path
from types import SimpleNamespace
import pytest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'contracts/NibbleRewriteForge.py'
HELPERS=[x for x in ast.parse(SOURCE.read_text()).body if isinstance(x,(ast.Assign,ast.FunctionDef))]
BASES={'blend':'Y X Y XOR C5 AND XOR','union':'X Y AND X Y XOR OR','cancel':'X Y SUB Y ADD'}
REWRITES={'blend':'X C5 AND Y C10 AND OR','union':'X Y OR','cancel':'X'}


def namespace(gl=None):
    ns=dict(hashlib=hashlib,json=json,re=re,gl=gl)
    exec(compile(ast.Module(body=HELPERS,type_ignores=[]),str(SOURCE),'exec'),ns)
    return ns


NS=namespace()


def reference(text):
    # Independent vector interpreter: each stack entry is the entire 256-case vector.
    inputs=list(itertools.product(range(16),repeat=2));stack=[]
    binary={'AND':operator.and_,'OR':operator.or_,'XOR':operator.xor,'ADD':operator.add,'SUB':operator.sub}
    unary={'NOT':operator.invert,'SHL1':lambda a:a*2,'SHR1':lambda a:a//2}
    for op in text.split():
        if op in ('X','Y'):stack.append([pair[0 if op=='X' else 1] for pair in inputs])
        elif op.startswith('C'):stack.append([int(op[1:])]*256)
        elif op in unary:stack.append([unary[op](x)%16 for x in stack.pop()])
        else:
            b,a=stack.pop(),stack.pop();stack.append([binary[op](x,y)%16 for x,y in zip(a,b)])
    assert len(stack)==1
    return stack[0]


def spec(text):
    p=NS['program'](text,40)
    return {'program':text,'source_cost':p['cost'],'semantics_root':NS['semantics_root'](reference(text)),'job_id':'test','owner':'creator','input_root':'bound'}


def test_all_1645_generated_expressions_match_independent_vector_interpreter():
    atoms=['X','Y','C0','C1','C5','C10','C15']
    expressions=atoms+[a+' '+op for a in atoms for op in ['NOT','SHL1','SHR1']]
    expressions += [a+' '+b+' '+op for a in atoms for b in atoms for op in ['AND','OR','XOR','ADD','SUB']]
    expressions += [a+' '+b+' '+op+' '+c+' ADD' for a in atoms for b in atoms for c in atoms for op in ['AND','XOR','SUB','OR']]
    assert len(expressions)==1645
    for text in expressions:assert NS['table'](NS['program'](text,40)['tokens'])==reference(text)


@pytest.mark.parametrize('text,expected',[('C15 C1 ADD',0),('C0 C1 SUB',15),('C0 NOT',15),('C15 SHL1',14),('C15 SHR1',7)])
def test_unsigned_wrap_shift_and_subtraction_order(text,expected):
    assert set(NS['table'](NS['program'](text,40)['tokens']))=={expected}


@pytest.mark.parametrize('text',['','X  Y ADD',' X','X ','X\n','C16','C00','C-1','X DUP','AND','X Y','X AND','__import__(os)','X '*40+'X'])
def test_malformed_programs_rejected(text):
    with pytest.raises((ValueError,TypeError)):NS['program'](text,40)


def test_stack_and_token_bounds():
    text=' '.join(['X']*17+['ADD']*16)
    with pytest.raises(ValueError,match='Stack bound'):NS['program'](text,40)
    with pytest.raises(ValueError):NS['program'](' '.join(['X']+['NOT']*24),24)


@pytest.mark.parametrize('name',list(BASES))
def test_known_rewrites_have_strict_cost_savings_and_full_equivalence(name):
    proof=NS['prove'](spec(BASES[name]),REWRITES[name])
    assert proof['checked_inputs']==256 and proof['cost']<proof['source_cost']
    assert proof['saved_model_units']==proof['source_cost']-proof['cost']
    assert proof['semantics_root']==spec(BASES[name])['semantics_root']


def test_distinct_valid_candidates_do_not_need_identical_syntax():
    a=NS['prove'](spec(BASES['blend']),'X C5 AND Y C10 AND OR')
    b=NS['prove'](spec(BASES['blend']),'X C5 AND Y C5 NOT AND OR')
    assert a['program']!=b['program'] and a['semantics_root']==b['semantics_root']


def test_single_bad_case_and_no_improvement_cannot_publish():
    with pytest.raises(ValueError,match='equivalent'):NS['prove'](spec(BASES['blend']),'X Y OR')
    with pytest.raises(ValueError,match='strict'):NS['prove'](spec(BASES['union']),BASES['union'])
    source=spec(BASES['cancel']);source['semantics_root']='f'*64
    with pytest.raises(ValueError,match='specification'):NS['prove'](source,'X')


def test_last_of_256_inputs_is_checked_not_just_a_sample():
    original='X X XOR'+' NOT'*20
    proposed='X Y AND X Y AND SHR1 AND X Y AND SHR1 SHR1 AND X Y AND SHR1 SHR1 SHR1 AND C1 AND'
    assert NS['program'](proposed,24)['cost']<NS['program'](original,40)['cost']
    assert reference(original)==[0]*256
    assert reference(proposed)==[0]*255+[1]
    with pytest.raises(ValueError,match='all 256'):NS['prove'](spec(original),proposed)


def deploy(vm,factory,actor):vm.sender=actor;return factory(str(SOURCE))
def optimize(c,vm,job,rewrite):
    vm.clear_mocks();vm.mock_llm('.*NIBBLE_REWRITE_V1.*',json.dumps({'program':rewrite}))
    return c.optimize(job,c.get_job(job)['input_root'])


def test_register_generate_publish_and_repeated_root_bound_evaluation(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=deploy(direct_vm,direct_deploy,direct_alice)
    job=c.register('blend',BASES['blend']);source=c.get_job(job)
    with direct_vm.expect_revert('No published'):c.evaluate(job,source['input_root'],1,2)
    root=optimize(c,direct_vm,job,REWRITES['blend']);artifact=c.get_artifact(job)
    assert root==artifact['root']
    direct_vm.sender=direct_bob
    expected=reference(BASES['blend'])
    for x in range(16):
        for y in range(16):assert c.evaluate(job,source['input_root'],x,y)['value']==expected[16*x+y]
    assert c.get_artifact(job)==artifact


def test_creator_context_replay_and_immutable_publication(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=deploy(direct_vm,direct_deploy,direct_alice);job=c.register('a',BASES['cancel']);s=c.get_job(job)
    direct_vm.sender=direct_bob
    with direct_vm.expect_revert('Only creator'):c.optimize(job,s['input_root'])
    peer=c.register('a',BASES['cancel']);assert peer!=job
    direct_vm.sender=direct_alice
    with direct_vm.expect_revert('Input root mismatch'):c.optimize(job,'f'*64)
    with direct_vm.expect_revert('Nonce already used'):c.register('a',BASES['blend'])
    optimize(c,direct_vm,job,'X')
    with direct_vm.expect_revert('Artifact already'):c.optimize(job,s['input_root'])
    with direct_vm.expect_revert('Input root mismatch'):c.evaluate(job,'f'*64,0,0)
    with direct_vm.expect_revert('Inputs must'):c.evaluate(job,s['input_root'],16,0)
    with direct_vm.expect_revert('Inputs must'):c.evaluate(job,s['input_root'],True,0)


def test_lowest_cost_guard_is_deterministic(direct_vm,direct_deploy,direct_alice):
    c=deploy(direct_vm,direct_deploy,direct_alice);job=c.register('floor','X')
    with direct_vm.expect_revert('No cheaper program'):c.optimize(job,c.get_job(job)['input_root'])
    with direct_vm.expect_revert('No published'):c.get_artifact(job)


@pytest.mark.parametrize('rewrite',['X Y OR','X Y AND X Y XOR OR','X DUP'])
def test_bad_model_never_creates_artifact(rewrite,direct_vm,direct_deploy,direct_alice):
    c=deploy(direct_vm,direct_deploy,direct_alice);job=c.register('bad',BASES['blend'])
    with direct_vm.expect_revert('LLM_ERROR'):optimize(c,direct_vm,job,rewrite)
    with direct_vm.expect_revert('No published'):c.get_artifact(job)
    assert optimize(c,direct_vm,job,REWRITES['blend'])==c.get_artifact(job)['root']


def test_actual_callback_independently_checks_candidate_substance_without_rerunning_generator():
    class Return:
        def __init__(self,x):self.calldata=x
    source=spec(BASES['blend']);calls=[]
    def llm(*args,**kwargs):calls.append('generate');return {'program':REWRITES['blend']}
    def run(leader,validator):
        honest=leader();assert validator(Return(honest)) is True
        alternate=NS['prove'](source,'X C5 AND Y C5 NOT AND OR');assert validator(Return(alternate)) is True
        forged=copy.deepcopy(honest);forged['program']='X Y OR'
        forged.update(cost=3,saved_model_units=source['source_cost']-3,instruction_count=3,peak_stack=2)
        forged['root']=NS['digest']({k:v for k,v in forged.items() if k!='root'})
        assert validator(Return(forged)) is False
        forged=copy.deepcopy(honest);forged['spec']['owner']='attacker';assert validator(Return(forged)) is False
        forged=copy.deepcopy(honest);forged['cost']=0;assert validator(Return(forged)) is False
        assert validator(Exception('LLM_ERROR')) is False
        return honest
    gl=SimpleNamespace(nondet=SimpleNamespace(exec_prompt=llm),vm=SimpleNamespace(Return=Return,run_nondet_unsafe=run,UserError=RuntimeError))
    assert namespace(gl)['synthesize'](source)['program']==REWRITES['blend']
    assert calls==['generate']


@pytest.mark.parametrize('raw',[None,{}, {'program':[]},{'program':'X','claimed_valid':True},'{"program":"X","program":"Y"}'])
def test_strict_candidate_json(raw):
    with pytest.raises((ValueError,TypeError)):NS['candidate'](raw)
