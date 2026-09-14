# Running and deploying ClaimBack

## Local judge demo

Follow the README. The offline Strands loop is the default. `CLAIMBACK_DB` optionally sets the SQLite path. Back up `runtime/claimback.db` if you want to preserve local demonstrations. Reset affects the current browser session only.

Optional web container:

```sh
docker build -t claimback-demo .
docker run --rm -p 8765:8765 claimback-demo
```

Container data is ephemeral unless you provision a writable persistent volume. The container recipes are provided but were not built in this environment. A public demo should remain in synthetic mode and should sit behind TLS and host-level rate limits. Bedrock mode should be private and authenticated before exposing it to avoid unbounded inference spend.

## AgentCore runtime entrypoint

The SDK entrypoint supports the AgentCore invocation contract and starts the runtime server on port 8080:

```sh
CLAIMBACK_MODE=demo python agentcore_entry.py
```

Send a local request:

```sh
curl http://localhost:8080/invocations -H 'Content-Type: application/json' \
  -d '{"case_id":"refund-1408","authorize_simulation":true}'
```

Use `warranty-349` for the second case. This entrypoint demonstrates a single fresh-case run, returning the partial-offer decision or the warranty follow-up state. It does not expose the full browser session lifecycle in the cloud.

## Bring the container to AgentCore

1. Select an AWS account and region, create a private ECR repository, and provision an AgentCore execution role using the official runtime permissions guidance. Do not embed credentials in the image.
2. Build `Dockerfile.agentcore` for **linux/arm64** and push it to your ECR repository. Use an immutable image digest for deployment.
3. In the AgentCore Runtime console, create an agent runtime using that image, HTTP protocol and the scoped execution role. Set `CLAIMBACK_MODE=demo` for a deterministic cloud smoke test.
4. Invoke with `{"case_id":"refund-1408","authorize_simulation":true}`. Confirm `synthetic=true`, six-tool orchestration capability, a human decision state and the returned audit trace. Capture the actual runtime ARN, deployment date and observed outcome in your submission only after it works.
5. For model-backed reasoning, grant only required Bedrock model invocation permissions and set `CLAIMBACK_MODE=bedrock`, `BEDROCK_MODEL_ID` and `AWS_REGION`. Keep merchant tools simulated until live authorization/persistence are implemented.
6. Inspect runtime logs in CloudWatch, use a budget/usage ceiling, and remove unused runtime/image resources after evaluation.

Example build (replace placeholders with your own account/repository):

```sh
docker buildx build --platform linux/arm64 -f Dockerfile.agentcore \
  -t <account>.dkr.ecr.<region>.amazonaws.com/<repository>:claimback-v1 --push .
```

AWS also documents direct Python code deployment and its AgentCore CLI. CLI generations differ; use the current official instructions rather than mixing older `configure/launch` commands with newer `create/deploy` commands.

## Needed for a persistent cloud product

The local UI is not currently routed to AgentCore. Add an authenticated API, DynamoDB optimistic revisions and outbox, S3 evidence storage with tenant access controls, a scheduler that respects next-check timestamps, and approved merchant integrations. Bind every invocation to authenticated tenant/case identity. Never trust a payload to assert that a real user authorized a settlement. The shipped standalone invocation does not accept arbitrary case state or settlement decisions.

Sources checked during implementation:

- [AgentCore Python direct deployment](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-code-deploy-python.html)
- [AgentCore CLI getting started](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-get-started-cli.html)
- [AgentCore runtime permissions](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-permissions.html)
- [Strands Python quickstart](https://strandsagents.com/docs/user-guide/quickstart/python/)

Deployment status: **verified on Amazon Bedrock AgentCore**. The runtime reached `READY`, and a signed synthetic invocation returned HTTP 200. See [AWS-DEPLOYED.md](AWS-DEPLOYED.md) for the deployment record, cost controls and current limitations.
