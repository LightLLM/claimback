# ClaimBack demo — target 4:40, maximum 5:00

Record the working local app at 1280×800 or larger, with synthetic mode visible. Reset first. Close unrelated tabs and notifications. Use the browser's normal scroll to show the whole decision card. No third-party music or assets are needed. Narration is approximately 470 words, leaving time for clicks and pauses. Rehearse and trim the actual recording to <=5:00; this script is not a recorded video.

| Time | Screen / action | Narration |
|---|---|---|
| 0:00–0:25 | Recovery desk, two cases | “A cancelled trip. A broken appliance. Getting your money back means finding receipts, reading policies and chasing replies. ClaimBack is for busy people who have a valid request but no time to manage another administrative loop.” |
| 0:25–0:45 | Show synthetic badge and amounts | “Our demo uses fictional companies and synthetic evidence. No real money moves. It runs through Strands Agents: the agent handles routine work, and the human keeps the final say.” |
| 0:45–1:15 | Northstar: Review & start → Authorize & start simulation | “Northstar cancelled a $1,408 trip. I authorize evidence gathering, the original claim, status checks and routine follow-up. I am not authorizing settlements. ClaimBack gathers the receipt, cancellation confirmation and policy, builds the request and submits it.” |
| 1:15–1:55 | Scroll to partial-offer card; open evidence briefly | “The company offers $880. The agent identifies a $528 shortfall and ties the challenge to the cancellation policy. This is where it stops. It cannot accept a settlement or waive rights. I can inspect every source, challenge the offer, or review exactly what accepting less means.” |
| 1:55–2:20 | Authorize challenge → Run agent | “I authorize the challenge. ClaimBack submits the policy-backed response and checks the next simulated reply. The full $1,408 refund is confirmed. The audit distinguishes what the agent did from what I decided.” |
| 2:20–2:55 | Forma: Review & start → Authorize & start simulation | “Now the warranty. The purifier failed within one year. The agent combines proof of purchase, the fault log and the warranty, then submits the package. After an explicitly simulated three-business-day advance, it sends a routine follow-up without asking me to write another message.” |
| 2:55–3:15 | Check response; show totals | “The replacement is confirmed. Notice the dashboard: $1,408 in simulated cash and $349 in non-cash replacement value. We keep those separate. Both administrative loops are completed.” |
| 3:15–3:45 | Evidence vault → draft; Agent activity → event details | “Every source has an ID and a hash. Every action has an actor, time and linked evidence. The complete case can be exported with its Strands tool transcript. This is a locally verifiable event chain, not a claim of immutable storage.” |
| 3:45–4:15 | Open architecture.svg | “Strands orchestrates six guarded tools. The demo model is scripted for repeatability; a Bedrock model can use the same tools. Authorization is enforced in code. We include an AgentCore entrypoint and deployment design; cloud deployment and live merchant integrations are not claimed here.” |
| 4:15–4:40 | Return to resolved recovery desk | “The product is about finishing the paperwork, not producing more of it. Next we will test with consenting users and measure completion, user time and actual recovery. ClaimBack gives routine work to the agent and consequential choices to the person. Get back to your life. We’ll chase the money.” |

## Recording checks

- Show both workflows working, not only slides.
- Keep the simulation label visible and state the cloud deployment status accurately.
- Show the authorization scope and the partial-offer card long enough to read.
- Read the full script aloud once; allow 20 seconds of safety margin under the five-minute cap.
- Upload the final video publicly to YouTube or Vimeo, verify anonymous access, and add the URL to Devpost.
- If a Bedrock run is recorded, label that mode and capture actual tool calls; do not splice scripted output into an apparent live-model run.
