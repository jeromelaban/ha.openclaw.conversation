# Research

- Collected: 2026-03-28
- Spec ID: 001-initial-feature

## Source: OpenClaw Gateway OpenAI HTTP API

URL: [OpenClaw Gateway OpenAI HTTP API](https://docs.openclaw.ai/gateway/openai-http-api)

### OpenClaw findings

1. OpenClaw exposes an OpenAI-compatible HTTP surface.
2. Documented endpoints include:
   - `GET /v1/models`
   - `GET /v1/models/{id}`
   - `POST /v1/chat/completions`
   - `POST /v1/embeddings`
   - `POST /v1/responses`
3. Authentication is bearer-token based through the gateway auth configuration.
4. The docs explicitly warn that this endpoint is an operator-access surface and should be kept on loopback, tailnet, or private ingress only.
5. The `model` field is agent-first, not provider-model-first.
6. `openclaw/default` is a stable default model identifier.
7. `openclaw/<agentId>` can target a specific agent.
8. The gateway can return `429` with `Retry-After` after repeated auth failures if rate limiting is configured.
9. Session behavior can be influenced by the OpenAI `user` field.
10. Extra compatibility headers exist, including `x-openclaw-model`, but these should be treated as advanced follow-up scope.

### OpenClaw relevance

These findings support the core concept of a Home Assistant integration that uses an OpenAI-compatible client with a custom `base_url` and OpenClaw model IDs.

## Source: Home Assistant `openai_conversation` integration

Reference: [homeassistant/components/openai_conversation](https://github.com/home-assistant/core/tree/dev/homeassistant/components/openai_conversation)

### Upstream integration findings

1. The upstream integration is a strong architectural starting point.
2. It already uses config entries, reauth flows, and multiple subentry types.
3. It validates setup with a lightweight model-list request.
4. It creates default subentries for:
   - conversation
   - ai_task_data
   - stt
   - tts
5. Runtime behavior uses the OpenAI Python client.
6. The current upstream implementation uses the Responses API path for prompt generation.
7. Many advanced model options are OpenAI-specific and should not be assumed to work with OpenClaw.

### Upstream integration relevance

This supports cloning the integration structure while narrowing the first scope to features backed by verified OpenClaw compatibility.

## Source: Home Assistant custom integration manifest docs

URL: [Integration manifest docs](https://developers.home-assistant.io/docs/creating_integration_manifest)

### Manifest findings

1. Custom integrations must include a `version` in `manifest.json`.
2. `config_flow: true` is required when a config flow exists.
3. `integration_type` should be set explicitly.
4. `documentation`, `issue_tracker`, `codeowners`, and `requirements` are standard manifest fields to define.
5. Manifest `domain` must match the integration directory name.
6. Custom integrations should only include requirements not already supplied by Home Assistant core.

### Manifest relevance

These rules define baseline manifest requirements for the future implementation and for HACS compatibility.

## Source: Home Assistant custom integration structure docs

URL: [Creating your first integration](https://developers.home-assistant.io/docs/creating_component_index)

### Integration structure findings

1. Custom integrations follow the same general architecture as core integrations.
2. A config-flow-capable scaffold is the standard path for new integrations.
3. Custom integrations live under `custom_components/<domain>/` and must include a manifest with a version.

### Integration structure relevance

This confirms the repository should be structured as a standard custom component, not as a Home Assistant add-on.

## Source: HACS integration publishing requirements

URL: [HACS integration publishing requirements](https://www.hacs.xyz/docs/publish/integration)

### HACS publishing findings

1. A HACS integration repository should contain exactly one integration under `custom_components/<domain>/`.
2. The repository should include `README.md` and `hacs.json`.
3. The integration `manifest.json` must define at least:
   - `domain`
   - `documentation`
   - `issue_tracker`
   - `codeowners`
   - `name`
   - `version`
4. Brand assets are required for validation.
5. GitHub releases are preferred but optional.

### HACS publishing relevance

These requirements determine the repository-level deliverables for the implementation phase.

## Source: HACS GitHub Action docs

URL: [HACS GitHub Action docs](https://www.hacs.xyz/docs/publish/action)

### HACS action findings

1. HACS provides a GitHub Action that validates repositories using HACS rules.
2. The action category for this project should be `integration`.
3. Recommended triggers include push, pull request, schedule, and workflow dispatch.
4. Ignorable checks exist, but the better starting point is to satisfy the default checks rather than disable them.

### HACS action relevance

This defines the minimum GitHub Action requirement requested in the feature brief.

## Source: Speckit / Spec Kit conventions

### Speckit findings

1. The numbered folder format `001-feature-name/` is a reasonable match for Speckit-style organization.
2. `spec.md` is the canonical core artifact.
3. `research.md` is a natural companion artifact.
4. `progress.md` is not a canonical requirement, but is a reasonable project-local extension.
5. Assumptions and open questions should be explicit rather than guessed away.

### Speckit relevance

This justifies the chosen folder layout and the inclusion of research/progress companion files.

## Outstanding Research Gaps

1. Whether OpenClaw fully supports the specific OpenAI Responses API behavior Home Assistant currently relies on.
2. Whether OpenClaw exposes enough compatibility for AI task features beyond basic conversation.
3. Whether self-signed TLS handling needs to be part of the initial scope.
4. Whether a model dropdown sourced from `/v1/models` is preferable to free-text entry in v1.
