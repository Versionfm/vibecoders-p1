"""Diagnostic counterfactuals: freeze the observed no-Read trigger, vary recovery only.

Each variant changes one input factor; all subsequent responses are live. This is
not end-to-end scoring, and the definition check below is only a reproduction signal.
"""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'src'))
from llm import get_chat_model, ModelReply
from tutor import answer_question
OUT=Path(__file__).resolve().parent
CAPTURED=json.loads((OUT.parent/'baseline.json').read_text())
TURN=CAPTURED['turns'][0]
QUESTION=TURN['result']['question']

class Instrumented:
 def __init__(self,variant):
  self.inner=get_chat_model();self.name=self.inner.name;self.thinking=self.inner.thinking
  self.variant=variant;self.calls=[]
 def chat(self,messages,temperature,tools=None):
  messages=[dict(m) for m in messages]
  if self.calls:
   # Locate the synthetic recovery message, preserving the real student's question.
   recovery=next(i for i,m in enumerate(messages) if m['role']=='user' and m['content'].startswith('Reconsider the original student request'))
   if self.variant=='bound_question':
    messages[recovery]['content']=messages[recovery]['content'].replace('the original student request','the current student request, reproduced here as JSON: '+json.dumps(QUESTION),1)
   elif self.variant=='drop_draft':
    del messages[recovery-1]
   elif self.variant=='drop_history':
    del messages[1:1+len(CAPTURED['seed_history'])]
   reply=self.inner.chat(messages,temperature,tools)
   source='live'
  else:
   assert messages==TURN['calls'][0]['messages']
   reply=ModelReply(TURN['calls'][0]['reply']['content']);source='recorded_trigger'
  self.calls.append({'messages':messages,'reply':asdict(reply),'source':source})
  return reply

def run(job):
 variant,repeat=job;model=Instrumented(variant);start=time.monotonic()
 result=answer_question(QUESTION,model,tutor='agentic',history=CAPTURED['seed_history'])
 row={'variant':variant,'repeat':repeat,'seconds':round(time.monotonic()-start,2),'result':asdict(result),'calls':model.calls}
 (OUT/f'{variant}_{repeat}.json').write_text(json.dumps(row,indent=2))
 print(variant,repeat,'error=',result.error,'definition=', 'Adaline (Adaptive Linear Neuron)' in result.answer,'original_reset=', 'The original request' in result.answer,'start=',result.answer[:180].replace('\n',' '),flush=True)
 return row
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=3) as pool:
  rows=list(pool.map(run,[(v,r) for v in ['baseline','bound_question','drop_draft','drop_history'] for r in range(1,4)]))
 print('Saved',len(rows),'diagnostic runs',flush=True)
