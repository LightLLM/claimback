"""All consequential state changes live here, outside the model's authority."""
import copy
import hashlib
import json
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data/synthetic_demo/cases.json"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def record(case, action, detail, actor="agent"):
    event = {"id": len(case["audit"]) + 1, "at": datetime.now(timezone.utc).isoformat(),
             "actor": actor, "action": action, "detail": detail,
             "previous_hash": case["audit"][-1]["hash"] if case["audit"] else "0" * 64}
    event["hash"] = digest(event)
    case["audit"].append(event)


def verify(case):
    previous = "0" * 64
    for event in case["audit"]:
        body = {k: v for k, v in event.items() if k != "hash"}
        if body["previous_hash"] != previous or digest(body) != event["hash"]:
            return False
        previous = event["hash"]
    return True


def initial_state():
    cases = json.loads(DATA.read_text(encoding="utf-8"))
    for case in cases:
        case.update(status="ready", authorized=False, gathered=False, eligible=None,
                    draft=None, decision=None, audit=[], messages=[], paid_cents=0, replacement_cents=0,
                    polls=0, followups=0, submission_id=None, appealed=False)
        for evidence in case["evidence"]:
            evidence["sha256"] = digest(evidence)
        record(case, "case_detected", "Synthetic case imported. No merchant contact authorized.", "system")
    return {"cases": cases, "revision": 0}


def get_case(state, case_id):
    for case in state["cases"]:
        if case["id"] == case_id:
            return case
    raise ValueError("Unknown case")


def authorize(case):
    if not case["authorized"]:
        case["authorized"] = True
        record(case, "authorization_granted", "User permits evidence gathering, original claim submission, status checks and one routine follow-up in the simulated merchant environment. No settlement or waiver authority.", "human")


def gather(case):
    if not case["gathered"]:
        case["gathered"] = True
        record(case, "evidence_gathered", {"sources": [e["id"] for e in case["evidence"]], "count": len(case["evidence"])})
    return copy.deepcopy(case["evidence"])


def assess(case):
    if not case["gathered"]:
        raise ValueError("Gather evidence before assessment")
    if case["kind"] == "warranty":
        days = (date.fromisoformat(case["issue_date"]) - date.fromisoformat(case["purchase_date"])).days
        eligible = 0 <= days <= case["warranty_days"] and len(case["evidence"]) >= 3
        reason = f"Fault reported {days} days after purchase; synthetic warranty covers {case['warranty_days']} days. Manufacturer review still required."
    else:
        eligible = {"receipt-ns", "cancel-ns", "policy-ns"}.issubset({e["id"] for e in case["evidence"]})
        reason = "Synthetic policy section 4 and merchant cancellation support requesting the full $1,408.00."
    if case["eligible"] is None:
        case["eligible"] = eligible
        record(case, "eligibility_assessed", {"eligible": eligible, "reason": reason})
    return {"eligible": eligible, "reason": reason, "source_ids": [e["id"] for e in case["evidence"]]}


def draft(case):
    if case["eligible"] is not True:
        raise ValueError("Verified demo eligibility required before drafting")
    if not case["draft"]:
        if case["kind"] == "refund":
            body = "Please refund USD 1,408.00 to the original payment method for booking NS-2048. Your cancellation confirmation establishes that Northstar cancelled the booking. Section 4 of your policy provides a full refund without a retained service fee. Attached: receipt-ns, cancel-ns, policy-ns. Please confirm the refund and processing timeline."
        else:
            body = "Please review warranty claim FM-7781 for a no-cost replacement. Purchased 2026-02-11; fault reported 2026-09-10, within the 365-day warranty. The owner reports no power after outlet testing, filter replacement and reset. Attached: receipt-fm, issue-fm, policy-fm. The fault has not been independently verified. Please confirm review status and any additional evidence required."
        case["draft"] = body
        record(case, "claim_drafted", {"body": body, "source_ids": [e["id"] for e in case["evidence"]]})
    return case["draft"]


def submit(case):
    if not case["authorized"] or not case["draft"] or case["eligible"] is not True:
        raise ValueError("Submission requires user authorization, eligibility and a draft")
    if case["submission_id"]:
        return {"submission_id": case["submission_id"], "duplicate_prevented": True}
    case["submission_id"] = "SIM-" + case["id"].upper()
    case["status"] = "submitted"
    record(case, "claim_submitted", {"adapter": "simulated", "submission_id": case["submission_id"], "body": case["draft"]})
    return {"submission_id": case["submission_id"]}


def monitor(case):
    if not case["submission_id"]:
        raise ValueError("Submit before checking status")
    if case["status"] in ("decision", "resolved", "settled"):
        return {"status": case["status"], "decision": case["decision"]}
    case["polls"] += 1
    if case["kind"] == "refund" and not case["appealed"]:
        case["status"] = "decision"
        case["decision"] = {"id": str(uuid.uuid4()), "kind": "partial_settlement",
                            "offered_cents": case["offer_cents"], "requested_cents": case["amount_cents"],
                            "gap_cents": case["amount_cents"] - case["offer_cents"],
                            "terms": "Accepting $880 closes this simulated refund case and gives up pursuing the remaining $528 in this demo.",
                            "recommendation": "Challenge the $528 shortfall using the cancellation policy. No outcome is guaranteed."}
        record(case, "partial_offer_received", case["decision"])
        record(case, "human_decision_required", "Model cannot accept, reject or waive settlement rights. Awaiting the user.")
    elif case["kind"] == "refund":
        case["status"] = "resolved"
        case["paid_cents"] = case["amount_cents"]
        record(case, "refund_confirmed", {"adapter": "simulated", "paid_cents": case["paid_cents"], "reference": "SIM-PAY-2048"})
    elif case["followups"]:
        case["status"] = "resolved"
        case["replacement_cents"] = case["amount_cents"]
        record(case, "replacement_confirmed", {"adapter": "simulated", "reference": "SIM-RMA-7781", "cash_paid_cents": 0, "replacement_value_cents": case["amount_cents"]})
    else:
        case["status"] = "waiting"
        record(case, "status_checked", "Simulated merchant: claim under review. Demo clock advanced 3 business days; routine follow-up is due.")
    return {"status": case["status"], "decision": case["decision"]}


def follow_up(case):
    if not case["authorized"] or case["status"] != "waiting":
        raise ValueError("Follow-up only permitted for an authorized pending claim")
    if not case["followups"]:
        case["followups"] = 1
        record(case, "follow_up_sent", {"adapter": "simulated", "body": "Please confirm review status for SIM-WARRANTY-349. The receipt, fault log and warranty policy were included. Please advise whether any further evidence is required."})
    return {"followups": case["followups"], "next": "Check status again"}


def decide(case, decision_id, choice, acknowledge=False):
    if case["status"] != "decision" or not case["decision"] or case["decision"]["id"] != decision_id:
        raise ValueError("Decision is stale or already handled")
    if choice not in ("challenge", "accept_partial"):
        raise ValueError("Unknown decision")
    if choice == "accept_partial" and not acknowledge:
        raise ValueError("Explicit acknowledgement of the $528 shortfall and closure is required")
    record(case, "human_decision", {"decision_id": decision_id, "choice": choice, "terms": case["decision"]["terms"]}, "human")
    if choice == "challenge":
        case["appealed"] = True
        case["status"] = "submitted"
        record(case, "challenge_submitted", {"adapter": "simulated", "body": "The offered USD 880.00 is USD 528.00 short of the USD 1,408.00 paid. Please reconsider under section 4; Northstar cancelled this booking. Sources: receipt-ns, cancel-ns, policy-ns. No settlement accepted or rights waived."})
    else:
        case["status"] = "settled"
        case["paid_cents"] = case["offer_cents"]
        record(case, "partial_settlement_confirmed", {"adapter": "simulated", "paid_cents": case["paid_cents"], "foregone_cents": case["amount_cents"] - case["paid_cents"]}, "system")
    case["decision"] = None
