# Decision policy

| Action | Allowed actor | Enforcement |
|---|---|---|
| Gather synthetic evidence | Agent after UI run authorization | Case bound in server tool factory |
| Assess fixture eligibility and build draft | Agent | Required evidence and eligibility preconditions |
| Submit original claim | Agent within explicit routine scope | `authorized`, `eligible` and `draft` required |
| Check status | Agent | Submission required; terminal/decision state stops progression |
| Routine follow-up | Agent within scope | Pending case only; one follow-up maximum |
| Challenge partial offer | Human | Current decision ID; recorded human action |
| Accept partial settlement | Human | Current decision ID + acknowledgement of shortfall/closure |
| Waive rights, agree to fees or new terms | Not available to model | No corresponding tool; future connector must escalate |

The $880 acceptance is explicitly a simulated settlement. The application never sends a real acceptance or moves money. Do not connect this anonymous demo API to real merchants. In a live service, replace the demo session with authenticated user identity, bind decisions to exact terms and expiration, record signed consent, and use per-action scopes, tenant authorization, rate limits and durable idempotency.

All evidence is data, not instructions. The agent prompt says this, while trusted tools compose outbound drafts from fixed fixture facts. A production document intake requires structured extraction and validation, provenance checks and review for ambiguous facts; merely adding a prompt instruction is not sufficient.
