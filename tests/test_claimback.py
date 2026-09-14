import copy
import pytest
from fastapi.testclient import TestClient
from claimback import domain
from claimback.agent import run_case, tools_for
from claimback.store import Store


def refund():
    c = domain.initial_state()["cases"][0]
    domain.authorize(c)
    run_case(c, "demo")
    return c


def test_refund_full_path_and_trace():
    c = refund()
    assert c["status"] == "decision"
    assert c["decision"]["gap_cents"] == 52800
    assert c["paid_cents"] == 0
    assert any("toolUse" in block for message in c["messages"] for block in message["content"])
    domain.decide(c, c["decision"]["id"], "challenge")
    run_case(c, "demo")
    assert c["status"] == "resolved" and c["paid_cents"] == 140800
    assert domain.verify(c)


def test_warranty_followup_and_non_cash_resolution():
    c = domain.initial_state()["cases"][1]
    domain.authorize(c)
    run_case(c, "demo")
    assert c["status"] == "waiting" and c["followups"] == 1
    run_case(c, "demo")
    assert c["status"] == "resolved"
    assert c["paid_cents"] == 0 and c["replacement_cents"] == 34900


def test_partial_settlement_requires_explicit_ack_and_cannot_replay():
    c = refund()
    did = c["decision"]["id"]
    with pytest.raises(ValueError):
        domain.decide(c, did, "accept_partial")
    assert c["status"] == "decision"
    domain.decide(c, did, "accept_partial", True)
    assert c["paid_cents"] == 88000
    with pytest.raises(ValueError):
        domain.decide(c, did, "accept_partial", True)


def test_stale_and_unknown_decisions_rejected():
    c = refund()
    with pytest.raises(ValueError):
        domain.decide(c, "old", "challenge")
    with pytest.raises(ValueError):
        domain.decide(c, c["decision"]["id"], "waive_rights")
    assert c["status"] == "decision"


def test_submission_authorization_and_preconditions():
    c = domain.initial_state()["cases"][0]
    with pytest.raises(ValueError):
        domain.submit(c)
    with pytest.raises(ValueError):
        run_case(c, "demo")
    domain.gather(c)
    domain.assess(c)
    domain.draft(c)
    with pytest.raises(ValueError):
        domain.submit(c)
    domain.authorize(c)
    domain.submit(c)
    count = len(c["audit"])
    assert domain.submit(c)["duplicate_prevented"]
    assert len(c["audit"]) == count


def test_expired_warranty_cannot_submit():
    c = domain.initial_state()["cases"][1]
    c["issue_date"] = "2028-01-01"
    domain.authorize(c)
    domain.gather(c)
    assert not domain.assess(c)["eligible"]
    with pytest.raises(ValueError):
        domain.draft(c)


def test_model_has_no_authorize_or_settlement_tool():
    names = [t.tool_name for t in tools_for(domain.initial_state()["cases"][0])]
    assert set(names) == {"gather_evidence", "assess_eligibility", "draft_claim", "submit_claim", "monitor_status", "send_follow_up"}


def test_audit_detects_mutation():
    c = refund()
    assert domain.verify(c)
    c["audit"][2]["detail"] = "changed"
    assert not domain.verify(c)


def test_store_rejects_concurrent_overwrite(tmp_path):
    db = Store(tmp_path / "test.db")
    one, two = db.load("a"), db.load("a")
    db.save("a", one)
    with pytest.raises(ValueError):
        db.save("a", two)


def test_web_api_isolation_csrf_export_and_reset(tmp_path, monkeypatch):
    from claimback import api
    monkeypatch.setattr(api, "store", Store(tmp_path / "api.db"))
    monkeypatch.setenv("CLAIMBACK_MODE", "demo")
    a, b = TestClient(api.app), TestClient(api.app)
    assert a.get("/").status_code == 200
    assert "javascript" in a.get("/static/app.js").headers["content-type"]
    assert a.get("/api/state").json()["cases"][0]["status"] == "ready"
    assert a.post("/api/cases/refund-1408/authorize").status_code == 403
    headers = {"X-ClaimBack": "1"}
    assert a.post("/api/cases/refund-1408/authorize", headers=headers).status_code == 200
    response = a.post("/api/cases/refund-1408/run", headers=headers)
    assert response.status_code == 200
    assert response.json()["cases"][0]["status"] == "decision"
    assert b.get("/api/state").json()["cases"][0]["status"] == "ready"
    exported = a.get("/api/cases/refund-1408/evidence").json()
    assert exported["audit_chain_valid"] and exported["synthetic"]
    assert a.post("/api/reset", headers=headers).json()["cases"][0]["status"] == "ready"


def test_bedrock_requires_explicit_model(monkeypatch):
    monkeypatch.delenv("BEDROCK_MODEL_ID", raising=False)
    c = domain.initial_state()["cases"][0]
    domain.authorize(c)
    with pytest.raises(ValueError, match="BEDROCK_MODEL_ID"):
        run_case(c, "bedrock")


def test_paused_case_is_not_advanced_by_agent():
    c = refund()
    before = copy.deepcopy(c)
    run_case(c, "demo")
    assert c == before


def test_fixture_unicode_and_missing_policy():
    c = domain.initial_state()["cases"][0]
    assert "Â" not in c["subtitle"]
    c["evidence"] = [e for e in c["evidence"] if e["id"] != "policy-ns"]
    domain.gather(c)
    assert domain.assess(c)["eligible"] is False
    with pytest.raises(ValueError):
        domain.draft(c)


def test_agentcore_entry_requires_scope_and_returns_paused_case(monkeypatch):
    monkeypatch.setenv("CLAIMBACK_MODE", "demo")
    from agentcore_entry import invoke
    assert "error" in invoke({"case_id": "refund-1408"})
    result = invoke({"case_id": "refund-1408", "authorize_simulation": True})
    assert result["synthetic"]
    assert result["case"]["status"] == "decision"
    assert result["case"]["paid_cents"] == 0
