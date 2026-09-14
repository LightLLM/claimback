"""AgentCore sandbox invocation. State is returned explicitly; no ephemeral-disk durability claim."""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from claimback.domain import initial_state, get_case, authorize
from claimback.agent import run_case

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload):
    # A standalone synthetic demonstration per invocation. No user state accepted,
    # no settlement endpoint exposed. Production persistence is a separate adapter.
    state = initial_state()
    case = get_case(state, payload.get("case_id", "refund-1408"))
    if payload.get("authorize_simulation") is not True:
        return {"error": "Explicit authorize_simulation=true required"}
    authorize(case)
    run_case(case)
    return {"synthetic": True, "case": case}


if __name__ == "__main__":
    app.run()
