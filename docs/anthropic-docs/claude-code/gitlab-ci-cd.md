---
source: https://code.claude.com/docs/en/gitlab-ci-cd
scraped: 2026-03-23
section: claude-code
---

# Claude Code GitLab CI/CD

> Learn about integrating Claude Code into your development workflow with GitLab CI/CD

Claude Code for GitLab CI/CD is currently in beta. This integration is maintained by GitLab. For support, see the [GitLab issue](https://gitlab.com/gitlab-org/gitlab/-/issues/573776).

This integration is built on top of the Claude Code CLI and Agent SDK.

## Why use Claude Code with GitLab?

- **Instant MR creation**: Describe what you need, and Claude proposes a complete MR with changes and explanation
- **Automated implementation**: Turn issues into working code with a single command or mention
- **Project-aware**: Claude follows your `CLAUDE.md` guidelines and existing code patterns
- **Simple setup**: Add one job to `.gitlab-ci.yml` and a masked CI/CD variable
- **Enterprise-ready**: Choose Claude API, AWS Bedrock, or Google Vertex AI
- **Secure by default**: Runs in your GitLab runners with your branch protection and approvals

## How it works

1. **Event-driven orchestration**: GitLab listens for your chosen triggers (for example, a comment mentioning `@claude` in an issue, MR, or review thread)
2. **Provider abstraction**: Use the provider that fits your environment (Claude API, AWS Bedrock, or Google Vertex AI)
3. **Sandboxed execution**: Each interaction runs in a container with strict network and filesystem rules

## Setup

### Quick setup

1. **Add a masked CI/CD variable**
   - Go to **Settings → CI/CD → Variables**
   - Add `ANTHROPIC_API_KEY` (masked, protected as needed)

2. **Add a Claude job to `.gitlab-ci.yml`**

```yaml
stages:
  - ai

claude:
  stage: ai
  image: node:24-alpine3.21
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  variables:
    GIT_STRATEGY: fetch
  before_script:
    - apk update
    - apk add --no-cache git curl bash
    - curl -fsSL https://claude.ai/install.sh | bash
  script:
    - /bin/gitlab-mcp-server || true
    - echo "$AI_FLOW_INPUT for $AI_FLOW_CONTEXT on $AI_FLOW_EVENT"
    - >
      claude
      -p "${AI_FLOW_INPUT:-'Review this MR and implement the requested changes'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
```

## Example use cases

```text
@claude implement this feature based on the issue description
@claude suggest a concrete approach to cache the results of this API call
@claude fix the TypeError in the user dashboard component
```

## Using with AWS Bedrock & Google Vertex AI

### AWS Bedrock workflow (OIDC)

**Required CI/CD variables:**
- `AWS_ROLE_TO_ASSUME`: ARN of the IAM role for Bedrock access
- `AWS_REGION`: Bedrock region (for example, `us-west-2`)

```yaml
claude-bedrock:
  stage: ai
  image: node:24-alpine3.21
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
  before_script:
    - apk add --no-cache bash curl jq git python3 py3-pip
    - pip install --no-cache-dir awscli
    - curl -fsSL https://claude.ai/install.sh | bash
    - export AWS_WEB_IDENTITY_TOKEN_FILE="${CI_JOB_JWT_FILE:-/tmp/oidc_token}"
    - if [ -n "${CI_JOB_JWT_V2}" ]; then printf "%s" "$CI_JOB_JWT_V2" > "$AWS_WEB_IDENTITY_TOKEN_FILE"; fi
    - >
      aws sts assume-role-with-web-identity
      --role-arn "$AWS_ROLE_TO_ASSUME"
      --role-session-name "gitlab-claude-$(date +%s)"
      --web-identity-token "file://$AWS_WEB_IDENTITY_TOKEN_FILE"
      --duration-seconds 3600 > /tmp/aws_creds.json
    - export AWS_ACCESS_KEY_ID="$(jq -r .Credentials.AccessKeyId /tmp/aws_creds.json)"
    - export AWS_SECRET_ACCESS_KEY="$(jq -r .Credentials.SecretAccessKey /tmp/aws_creds.json)"
    - export AWS_SESSION_TOKEN="$(jq -r .Credentials.SessionToken /tmp/aws_creds.json)"
  script:
    - /bin/gitlab-mcp-server || true
    - >
      claude
      -p "${AI_FLOW_INPUT:-'Implement the requested changes and open an MR'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
  variables:
    AWS_REGION: "us-west-2"
```

### Google Vertex AI workflow (Workload Identity Federation)

**Required CI/CD variables:**
- `GCP_WORKLOAD_IDENTITY_PROVIDER`: Full provider resource name
- `GCP_SERVICE_ACCOUNT`: Service account email
- `CLOUD_ML_REGION`: Vertex region (for example, `us-east5`)

```yaml
claude-vertex:
  stage: ai
  image: gcr.io/google.com/cloudsdktool/google-cloud-cli:slim
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web"'
  before_script:
    - apt-get update && apt-get install -y git && apt-get clean
    - curl -fsSL https://claude.ai/install.sh | bash
    - gcloud auth login --cred-file=<(cat <<EOF
      {
        "type": "external_account",
        "audience": "${GCP_WORKLOAD_IDENTITY_PROVIDER}",
        "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
        "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/${GCP_SERVICE_ACCOUNT}:generateAccessToken",
        "token_url": "https://sts.googleapis.com/v1/token"
      }
      EOF
      )
  script:
    - /bin/gitlab-mcp-server || true
    - >
      CLOUD_ML_REGION="${CLOUD_ML_REGION:-us-east5}"
      claude
      -p "${AI_FLOW_INPUT:-'Review and update code as requested'}"
      --permission-mode acceptEdits
      --allowedTools "Bash Read Edit Write mcp__gitlab"
      --debug
  variables:
    CLOUD_ML_REGION: "us-east5"
```

## Best practices

### CLAUDE.md configuration

Create a `CLAUDE.md` file at the repository root to define coding standards, review criteria, and project-specific rules.

### Security considerations

**Never commit API keys or cloud credentials to your repository**. Always use GitLab CI/CD variables:
- Add `ANTHROPIC_API_KEY` as a masked variable
- Use provider-specific OIDC where possible (no long-lived keys)
- Limit job permissions and network egress
- Review Claude's MRs like any other contributor

### CI costs

- **GitLab Runner time**: Claude runs on your GitLab runners and consumes compute minutes
- **API costs**: Each Claude interaction consumes tokens based on prompt and response size
- **Cost optimization tips**: Use specific `@claude` commands, set appropriate `max_turns` and job timeout values, limit concurrency

## Security and governance

- Each job runs in an isolated container with restricted network access
- Claude's changes flow through MRs so reviewers see every diff
- Branch protection and approval rules apply to AI-generated code
- Claude Code uses workspace-scoped permissions to constrain writes

## Troubleshooting

### Claude not responding to @claude commands

- Verify your pipeline is being triggered
- Ensure CI/CD variables are present and unmasked
- Check that the comment contains `@claude` (not `/claude`)

### Job can't write comments or open MRs

- Ensure `CI_JOB_TOKEN` has sufficient permissions, or use a Project Access Token with `api` scope
- Check the `mcp__gitlab` tool is enabled in `--allowedTools`

### Authentication errors

- **For Claude API**: Confirm `ANTHROPIC_API_KEY` is valid and unexpired
- **For Bedrock/Vertex**: Verify OIDC/WIF configuration, role impersonation, and secret names

## Advanced configuration

### Common parameters and variables

- `prompt` / `prompt_file`: Provide instructions inline (`-p`) or via a file
- `max_turns`: Limit the number of back-and-forth iterations
- `timeout_minutes`: Limit total execution time
- `ANTHROPIC_API_KEY`: Required for the Claude API (not used for Bedrock/Vertex)

### Customizing Claude's behavior

1. **CLAUDE.md**: Define coding standards, security requirements, and project conventions
2. **Custom prompts**: Pass task-specific instructions via `prompt`/`prompt_file` in the job
