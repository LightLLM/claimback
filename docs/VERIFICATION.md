# Verification record

Local build verification: September 13, 2026 (Pacific).

## Automated

`python -m pytest -q`: **14 passed** with two upstream deprecation warnings (Starlette/AnyIO and AgentCore/Pydantic). Python 3.11 on Windows. `node --check frontend/app.js` also passed.

The suite covers:

1. Refund submission, partial-offer pause, human challenge and full simulated confirmation, including actual Strands tool-use messages.
2. Warranty submission, one follow-up, status continuation and non-cash replacement.
3. Partial acceptance acknowledgement and rejection of replayed decisions.
4. Stale IDs and unknown decision actions.
5. Submission authorization, prerequisites and duplicate prevention.
6. Expired warranty rejection.
7. Absence of model authorization/settlement tools.
8. Audit-chain mutation detection.
9. Optimistic concurrent-write rejection.
10. Browser-session isolation, same-origin request header requirement, JavaScript MIME type, evidence export and reset.
11. Explicit Bedrock model configuration requirement.
12. Agent cannot advance a paused decision case.
13. UTF-8 fixture handling and missing-policy rejection.
14. AgentCore standalone entrypoint scope and paused-case return.

## Browser verification

Used the running app in the Codex browser, not static mockups:

- Opened scoped authorization and started the refund.
- Inspected the $880 offer and $528 shortfall card.
- Opened partial-settlement review, clicked acceptance without acknowledgement, and observed the blocking explanation.
- Closed the review, authorized the challenge and ran the next status check; observed $1,408 simulated cash recovered.
- Started the warranty; observed submitted evidence and one follow-up, then checked the response and observed $349 replacement value with cash unchanged.
- Reloaded after server restart and observed both persisted outcomes.
- Reset the demo to fresh cases.

Browser testing found and fixed Windows `.js` MIME registration (strict browsers blocked JavaScript served as text/plain) and implicit Windows text encoding for fixture loading. Regression assertions were added.

## AgentCore local runtime

Started `python agentcore_entry.py` and successfully posted a synthetic authorized refund invocation to `http://127.0.0.1:8080/invocations`. Response returned `synthetic=true` and `case.status=decision` with an audit trace. This checks the local SDK HTTP contract, not deployment to AWS.

## Not verified

AWS Bedrock inference, deployed AgentCore runtime, Docker image builds, Linux CI execution, live merchant integrations, public hosting and production security/load characteristics. The repository includes relevant entrypoints, recipes and design notes without claiming these have run. All tested financial outcomes are synthetic.
