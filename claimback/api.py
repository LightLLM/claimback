import os
import mimetypes
import re
import secrets
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from . import domain
from .agent import run_case
from .store import Store

ROOT = Path(__file__).resolve().parent.parent
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
app = FastAPI(title="ClaimBack", version="0.1.0")
store = Store()


@app.middleware("http")
async def session_boundary(request: Request, call_next):
    sid = request.cookies.get("claimback_session", "")
    fresh = not re.fullmatch(r"[a-f0-9]{64}", sid)
    if fresh:
        sid = secrets.token_hex(32)
    request.state.session = sid
    if request.method == "POST" and request.headers.get("x-claimback") != "1":
        return JSONResponse({"detail": "Same-origin application request required"}, status_code=403)
    response = await call_next(request)
    if fresh:
        response.set_cookie("claimback_session", sid, httponly=True, samesite="strict", secure=request.url.scheme == "https")
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'self'"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(ValueError)
async def bad_request(request, error):
    return JSONResponse({"detail": str(error)}, status_code=409)


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision_id: str
    choice: str
    acknowledge: bool = False


@app.get("/api/state")
def state(request: Request):
    data = store.load(request.state.session)
    data["mode"] = os.getenv("CLAIMBACK_MODE", "demo")
    data["merchant_adapter"] = "simulated"
    return data


@app.post("/api/cases/{case_id}/authorize")
def authorize(case_id: str, request: Request):
    data = store.load(request.state.session)
    domain.authorize(domain.get_case(data, case_id))
    store.save(request.state.session, data)
    return data


@app.post("/api/cases/{case_id}/run")
def run(case_id: str, request: Request):
    data = store.load(request.state.session)
    case = domain.get_case(data, case_id)
    try:
        run_case(case)
    except ValueError:
        raise
    except Exception:
        domain.record(case, "agent_run_failed", "Run failed; inspect server logs or model configuration. No live merchant action was performed.", "system")
        store.save(request.state.session, data)
        raise HTTPException(503, "Agent unavailable. Check model configuration and retry; completed simulated steps are preserved.")
    store.save(request.state.session, data)
    return data


@app.post("/api/cases/{case_id}/decision")
def decision(case_id: str, body: Decision, request: Request):
    data = store.load(request.state.session)
    domain.decide(domain.get_case(data, case_id), body.decision_id, body.choice, body.acknowledge)
    store.save(request.state.session, data)
    return data


@app.get("/api/cases/{case_id}/evidence")
def export(case_id: str, request: Request):
    case = domain.get_case(store.load(request.state.session), case_id)
    return JSONResponse({"synthetic": True, "case": case, "audit_chain_valid": domain.verify(case),
                         "integrity_note": "Hash linkage detects local edits; not externally anchored or immutable."},
                        headers={"Content-Disposition": f'attachment; filename="{case["id"]}-evidence.json"'})


@app.post("/api/reset")
def reset(request: Request):
    old = store.load(request.state.session)
    data = domain.initial_state()
    data["revision"] = old["revision"]
    store.save(request.state.session, data)
    return data


@app.get("/health")
def health():
    return {"status": "ok", "mode": os.getenv("CLAIMBACK_MODE", "demo")}


@app.get("/")
def index():
    return FileResponse(ROOT / "frontend/index.html")


app.mount("/static", StaticFiles(directory=ROOT / "frontend"), name="static")
