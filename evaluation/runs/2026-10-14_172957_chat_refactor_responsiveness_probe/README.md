# Preserved failed responsiveness probe

Before any full evaluation, the Agentic Tutor responsiveness probe failed in 0.532 s before any Read. Two short diagnostic calls also failed. The error was `APIConnectionError` caused by `ConnectError: [Errno -2] Name or service not known`.

The configured hostname was `api.deepseek.comz` (an extra trailing z). The official hostname and public control both resolved, so this was a local endpoint configuration typo. The main session corrected that single hostname in the local `.env`; model and thinking settings were unchanged. No evaluation cases were run or scored under the typo.

The subsequent successful probe is preserved separately in `evaluation/runs/2026-10-14_173145_chat_refactor_responsiveness_probe/probe.json`: 2.505 s; Agentic Tutor read PEID, cited PEID-1.3, and completed an answer without errors or reaching the Read limit. Probe findings establish responsiveness only, not Golden Set quality.
