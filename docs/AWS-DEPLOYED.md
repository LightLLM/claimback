# Verified AWS deployment — September 14, 2026

ClaimBack's standalone synthetic agent is deployed to Amazon Bedrock AgentCore Runtime in us-east-1.

- Runtime ID: ClaimBackDemo-Lx4m1f6TZR
- Runtime ARN: arn:aws:bedrock-agentcore:us-east-1:134553439892:runtime/ClaimBackDemo-Lx4m1f6TZR
- Version: 1
- Runtime status: READY
- Direct deployment: Python 3.11, ARM64 dependencies, private S3 code archive.
- Authentication: AWS IAM. This is not an anonymous public web URL.
- Mode: scripted synthetic Strands agent. No Bedrock model permissions or real merchant actions.
- Idle timeout: 60 seconds; maximum session lifetime: 300 seconds.

Verified cloud invocation returned HTTP 200, synthetic=true, refund case status=decision, and the $528 shortfall decision. The test session was explicitly stopped afterwards.

## Cost boundary

The account reports FREE / ACTIVE with USD 120 remaining credits and expiration December 3, 2026 at 06:38 UTC. No account upgrade was performed. AWS documents that the Free account plan prevents charges while active; resource use consumes credits. This is not an always-free AgentCore service, and billing/credit reporting can lag.

No paid inference, NAT gateway, load balancer, public website, container build service or scheduled workload was provisioned. Resources created: private S3 bucket claimback-demo-134553439892-use1 with agent.zip, IAM role ClaimBackDemoRuntime with scoped policy, and the AgentCore runtime and associated workload identity. Runtime logging may create CloudWatch log resources.

## Scope

The browser UI remains local. The deployed endpoint starts a fresh synthetic case per invocation and returns the trace; durable multi-step cloud state and UI integration are not implemented.

## Re-run

Use AWS CLI invoke-agent-runtime with the ARN above, a unique session ID of at least 33 characters and a payload file containing {"case_id":"refund-1408","authorize_simulation":true}. Use stop-runtime-session afterwards, or allow the 60-second idle timeout. The warranty fixture ID is warranty-349.

## Cleanup

Delete this AgentCore runtime, its associated workload identity if retained, the agent.zip object and its dedicated bucket, and the role's ClaimBackDemoMinimal inline policy then the ClaimBackDemoRuntime role. Inspect runtime-specific CloudWatch log groups for retention/deletion. Do not delete unrelated account resources.

AWS Free plan reference: https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html
