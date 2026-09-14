# ClaimBack

## Tagline
Get back to your life. We’ll chase the money.

## Elevator pitch
ClaimBack is a Strands-powered recovery agent that assembles refund and warranty evidence, submits authorized claims and follows up, while leaving settlements and compromises to the human.

## Inspiration
Getting money back is rarely one task. It is finding a receipt, locating the right policy, explaining what happened, chasing a reply, and deciding whether an offer is fair. Busy consumers often leave that loop unfinished. We wanted an agent that owns the routine work while making the moments that need human judgment unmistakable.

## What it does
ClaimBack presents a recovery desk with two complete synthetic stories. In the first, a cancelled $1,408 trip produces an $880 offer. The agent gathers the receipt, merchant cancellation and policy, submits the claim and surfaces the $528 discrepancy. It pauses. The user can authorize a challenge or explicitly acknowledge the consequences of accepting the partial settlement.

In the second, a $349 air purifier fails within its warranty period. The agent assembles proof of purchase, a fault log and policy, submits the claim, follows up and checks for a replacement confirmation. Replacement value stays separate from cash recovered.

Every case includes readable evidence, a source-backed claim draft and a timestamped audit export. All companies, policies and outcomes in this demonstration are synthetic; no real merchant messages or payments occur.

## How we built it
The core uses the Python Strands Agents SDK with six tools: gather evidence, assess eligibility, draft claim, submit claim, monitor status and send follow-up. Tools are bound to a single case, execute sequentially, and enforce authorization and state transitions outside model prompts. The model has no settlement or authorization tool.

The default scripted model provider runs the real Strands tool loop without credentials, making the demo reproducible. A configurable Amazon Bedrock model uses the same tools for model-driven orchestration. Bedrock inference remains optional and was not used in the deployed synthetic demonstration.

A small FastAPI service persists browser-scoped state in SQLite with optimistic concurrency. The responsive web UI uses no frontend build chain. The standalone synthetic Strands agent is deployed on Amazon Bedrock AgentCore Runtime in `us-east-1` and returned HTTP 200 in a verified cloud invocation. The browser UI remains local; durable cloud state and live merchant integrations are future work.

## Challenges
The hardest design question was authority: routine recovery work should proceed, but an agent must not convert a merchant offer into a user's consent. We solved that with a separate human decision endpoint, current decision IDs and explicit acknowledgement for partial settlement. We also separate claimed value, confirmed simulated cash, and non-cash replacement value so the dashboard never inflates its results.

## Accomplishments
Two working end-to-end flows share the same Strands tools and policy layer. The app can demonstrate evidence gathering, authorized submission, follow-up, a human escalation, and an outcome with an inspectable trail. Tests cover both flows, duplicate prevention, approval replay rejection, unauthorized submission, expired warranty rejection, session isolation and audit mutation detection.

## What we learned
An agent's useful output is a completed administrative step with evidence and a clear authority boundary. A concise decision card can communicate more effectively than a long chat transcript when a person needs to make one consequential choice.

## What's next
Pilot with consenting consumers, add authenticated source/merchant connectors and durable cloud state, then measure case completion, active user time, unnecessary interruptions and actual recovered value. Extend the same workflow to reimbursements and other claims only after adding the appropriate policy and approval rules.

## Built with
Python, Strands Agents SDK, Amazon Bedrock integration, Amazon Bedrock AgentCore SDK, FastAPI, SQLite, HTML, CSS, JavaScript, pytest.

## Testing instructions
Clone the public repository, install `requirements.txt`, and run `python -m uvicorn claimback.api:app --host 127.0.0.1 --port 8765`. Open the local address. Use Review & start for each case. On the refund, authorize the challenge then Run agent. On the warranty, Check response after the first run. The README contains the complete flow and alternative partial-settlement path. No paid account is required for offline judging.

## Fields the entrant must complete
- Public repository URL: **https://github.com/LightLLM/claimback**
- Public YouTube/Vimeo video: **IN PROGRESS — add the public YouTube URL after recording (at most five minutes)**
- AWS Builder ID: **[ENTRANT TO PROVIDE — AWS account 134553439892 is recorded separately as deployment evidence]**
- Submitter type: **Individual**
- Country of residence: **Canada**
- Optional live demo URL: **[ADD ONLY IF DEPLOYED]**
- AgentCore deployment: **Verified READY runtime; see docs/AWS-DEPLOYED.md**
- Track: **Everyday Agents**
- Team and pre-existing work disclosure: **[REVIEW FOR ACCURACY]**

Before submission, remove this administrative section, replace placeholders, and update any verification/deployment statements only with actual results. Do not claim real recovered money or live merchant integrations.
