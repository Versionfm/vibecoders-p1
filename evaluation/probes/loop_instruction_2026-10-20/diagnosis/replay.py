"""Offline replay of the recorded failure, through the app's real answer function.

This catches the captured symptom; it cannot predict a model response to changed prompts.
Use --payload-only for the smaller recovery-request invariant check.
"""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'src'))
from llm import ModelReply, ToolCall
from tutor import answer_question

captured = json.loads((Path(__file__).resolve().parents[1] / 'baseline.json').read_text())
turn = captured['turns'][0]

class Replay:
    name = 'recorded-deepseek-flash'
    thinking = False
    def __init__(self):
        self.calls = []
    def chat(self, messages, temperature, tools=None):
        index = len(self.calls)
        self.calls.append(messages)
        actual = turn['calls'][index]
        assert messages == actual['messages'], 'Request differs from captured trace: live validation required'
        reply = actual['reply']
        return ModelReply(reply['content'], [ToolCall(**call) for call in reply['tool_calls']])

model = Replay()
result = answer_question(turn['result']['question'], model, tutor='agentic', history=captured['seed_history'])
assert result.error is None, result.error
assert result.answer == turn['result']['answer'], 'Replay must reproduce exact captured output'
print('Replayed actual failure through answer_question:', len(model.calls), 'model calls; GAIF read once')
if '--payload-only' in sys.argv:
    latest_user = next(m['content'] for m in reversed(model.calls[1]) if m['role'] == 'user')
    print('Latest recovery user message:', latest_user)
    assert turn['result']['question'] in latest_user, 'Recovery replaces current question with an unbound original-request instruction'
else:
    print('Final answer starts:', result.answer.splitlines()[0])
    assert 'The original request' not in result.answer, 'Asked What is adaline; returned original gradient-descent task'
    assert 'Adaline (Adaptive Linear Neuron)' in result.answer, 'Definition of requested concept is missing'
