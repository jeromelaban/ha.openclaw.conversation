# OpenClaw Conversation

- Status: In progress
- Created: 2026-03-28
- Last updated: 2026-03-29
- Spec ID: 001-initial-feature
- Type: Initial feature spec

## Summary

Build a new Home Assistant custom component named **OpenClaw Conversation** that is derived from the upstream `openai_conversation` integration pattern, but allows a configurable OpenAI-compatible API endpoint so Home Assistant can use a self-hosted OpenClaw Gateway as its LLM provider.

The integration will be distributed as a HACS-compatible custom integration repository with GitHub Actions enabled for repository validation and Home Assistant integration checks.

## Problem Statement

Home Assistant already ships an `openai_conversation` integration, but it assumes OpenAI-hosted endpoints and credentials. OpenClaw exposes an OpenAI-compatible HTTP API, including `/v1/models`, `/v1/chat/completions`, `/v1/responses`, and `/v1/embeddings`, which makes it a viable self-hosted LLM target for Home Assistant.

There is currently no dedicated custom integration that:

1. Lets a user configure a custom OpenAI-compatible base URL for OpenClaw.
2. Preserves the Home Assistant conversation-agent experience.
3. Ships as a standalone custom integration repository suitable for HACS custom repositories.
4. Documents the security and operator-token implications of the OpenClaw Gateway endpoint.

## Goals

1. Create a custom integration named `openclaw_conversation` for Home Assistant.
2. Reuse the architecture and user experience of `openai_conversation` where it makes sense.
3. Add configuration for a custom API base URL and API token.
4. Allow Home Assistant to use OpenClaw as a configured LLM for conversation and AI task generation.
5. Package the repository so it is compatible with HACS custom integration repositories.
6. Define required GitHub Actions for validation and CI.
7. Keep the initial implementation narrow and low-risk by only specifying capabilities verified by research.

## Non-Goals

1. Building the integration implementation in this phase.
2. Publishing a Supervisor add-on or add-on repository.
3. Supporting public-internet exposure of the OpenClaw Gateway.
4. Guaranteeing support for OpenAI features not confirmed by OpenClaw docs, such as image generation, STT, or TTS.
5. Reworking Home Assistant core behavior outside the custom integration boundary.

## Assumptions

1. The repository target is a **HACS-compatible custom integration repository**, even though the initial request used the phrase "HA addons custom repository".
2. OpenClaw's OpenAI-compatible HTTP surface is enabled by the gateway operator.
3. The integration will authenticate with a single bearer token/password-equivalent credential supplied by the user.
4. The initial release should focus on LLM conversation use cases first, not media-generation or voice features.
5. OpenClaw's `/v1/responses` and `/v1/models` endpoints are sufficiently compatible with the OpenAI Python client used by Home Assistant patterns.

## User Scenarios

### Scenario 1: Add OpenClaw as a conversation provider

As a Home Assistant user, I want to add my OpenClaw Gateway URL and token in a config flow so I can use my self-hosted OpenClaw instance as a conversation agent.

#### Acceptance criteria for adding OpenClaw

- The config flow asks for a base URL and API token.
- The connection is validated before the entry is created.
- Authentication failures are reported as invalid credentials.
- Connection failures are reported as cannot connect.
- A successful setup creates a usable config entry and default conversation-related subentries.

### Scenario 2: Use a specific OpenClaw agent target

As a Home Assistant user, I want to choose a model identifier such as `openclaw/default` or `openclaw/<agentId>` so prompts route to the correct OpenClaw agent.

#### Acceptance criteria for agent selection

- The integration defaults to `openclaw/default`.
- The selected model identifier is stored in options/subentries.
- Requests send the selected model identifier unchanged unless the spec later defines normalization.
- The integration does not require raw upstream provider model IDs.

### Scenario 3: Keep Home Assistant prompt customization

As a Home Assistant user, I want the same prompt and Home Assistant API exposure options that similar HA conversation integrations provide so I can tune the assistant behavior without editing YAML.

#### Acceptance criteria for prompt customization

- Conversation subentries support prompt customization.
- Conversation subentries support choosing available Home Assistant LLM APIs.
- Recommended defaults are created during initial setup.

### Scenario 4: Install from a custom repository

As a Home Assistant user, I want to add the repository as a custom repository in HACS and install it cleanly.

#### Acceptance criteria for HACS installation

- The repository contains exactly one integration under `custom_components/openclaw_conversation/`.
- The repository includes `hacs.json` and required metadata.
- The GitHub repository has a non-empty description and valid repository topics configured.
- The repository includes brand assets required for HACS validation.
- CI includes HACS validation.

## Functional Requirements

### FR-1: Integration identity

1. The Home Assistant integration domain must be `openclaw_conversation`.
2. The integration name shown to users must be `OpenClaw Conversation`.
3. The repository must contain a single custom integration rooted at `custom_components/openclaw_conversation/`.

### FR-2: Config flow inputs

1. The initial config flow must ask for:
   - `base_url`
   - `api_key` or equivalent bearer-token field
2. The base URL must target the OpenClaw OpenAI-compatible API surface.
3. The UX must clearly indicate that the expected URL is the API root ending in `/v1`.
4. Reauthentication must allow updating credentials without deleting the entry.

### FR-3: Connection validation

1. Validation must attempt a lightweight authenticated API call before entry creation.
2. The preferred validation call is model listing against the OpenAI-compatible models endpoint.
3. Authentication failures must map to an invalid-auth error.
4. Network and transport failures must map to a cannot-connect error.
5. Rate-limit or disabled-endpoint responses must surface as actionable setup errors.

### FR-4: Runtime client behavior

1. The integration must construct its OpenAI-compatible client with a configurable base URL instead of assuming OpenAI defaults.
2. The integration must use the configured bearer token for all requests.
3. The initial runtime path must target APIs already documented by OpenClaw as supported.
4. The first implementation target is Home Assistant conversation and AI-task style prompt generation.

### FR-5: Conversation feature scope

1. The initial feature set must include a conversation-capable subentry equivalent.
2. The initial feature set should include AI task generation only if it can use the same validated OpenClaw-compatible request path.
3. The spec must explicitly defer STT, TTS, and image-generation features until compatibility is proven.
4. The default conversation model must be `openclaw/default`.
5. The integration must allow overriding the model target with another OpenClaw agent identifier.

### FR-6: Option model parity with upstream where safe

1. The component should mirror `openai_conversation` setup patterns where that reduces maintenance risk.
2. Prompt customization and Home Assistant LLM API selection must be preserved.
3. Upstream OpenAI-only advanced settings must be reviewed individually rather than copied blindly.
4. Options that depend on OpenAI-specific product behavior must be excluded from the initial release unless confirmed compatible with OpenClaw.

### FR-7: Security UX

1. Documentation and config-flow descriptions must warn that OpenClaw Gateway bearer credentials are operator-level credentials.
2. Documentation must recommend loopback, tailnet, or private-network exposure only.
3. The spec must avoid implying the endpoint is safe for public anonymous or lightly scoped access.

### FR-8: Repository compatibility

1. The repository must be valid for a HACS custom integration repository.
2. The repository must include:
   - `custom_components/openclaw_conversation/`
   - `README.md`
   - `hacs.json`
   - brand assets
   - GitHub workflow files
3. The integration manifest must include at least the fields required for custom integrations and HACS validation.
4. The manifest must include a custom-integration `version`.
5. The manifest must declare `config_flow: true`.
6. The integration manifest must include `documentation` and `issue_tracker` URLs.
7. The integration manifest `iot_class` must use a value accepted by Home Assistant validation.
8. The repository must define a GitHub description and HACS-valid repository topics in repository settings.

### FR-8a: Config-entry-only setup

1. The integration must declare itself as config-entry-only for Home Assistant validation.
2. The module-level setup contract must match the absence of YAML configuration support.

### FR-9: GitHub Actions

1. The repository must include a HACS validation workflow using the HACS GitHub Action with category `integration`.
2. The repository must include a Home Assistant validation workflow such as `hassfest`.
3. The repository should include a test/lint workflow appropriate for a Home Assistant custom integration repository.
4. Workflows must run on push, pull request, and manual dispatch; scheduled validation is recommended.

## Edge Cases

1. User enters a gateway URL without `/v1`.
2. User enters a URL with a trailing slash or double `/v1/` path.
3. OpenClaw endpoint is reachable but the OpenAI-compatible surface is disabled.
4. Token is valid syntactically but rejected by gateway auth.
5. Gateway rate-limits repeated failed authentication attempts and returns `429`.
6. Model list returns only OpenClaw agent identifiers rather than raw provider models.
7. User expects OpenAI STT/TTS/image features that OpenClaw does not expose.
8. Self-signed TLS or private CA deployments may fail certificate validation.

## Repository Shape

```text
custom_components/
  openclaw_conversation/
    __init__.py
    manifest.json
    config_flow.py
    const.py
    conversation.py
    ai_task.py
    strings.json
    translations/
    services.yaml (only if needed)
.github/
  workflows/
README.md
hacs.json
```

This shape is the intended implementation target, not a commitment that every listed file must ship in the first code change.

## Success Criteria

1. A Home Assistant user can install the repository from HACS as a custom repository.
2. A user can add the integration with a private OpenClaw Gateway URL and token.
3. Home Assistant can successfully validate the endpoint and create a config entry.
4. The integration can act as an LLM-backed conversation provider using `openclaw/default`.
5. The repository passes HACS validation and Home Assistant metadata validation in CI.
6. The documentation makes the private-network and operator-token security model clear.
7. The repository metadata required by HACS is present both in-repo and in GitHub repository settings.

## Risks

1. Upstream `openai_conversation` may rely on OpenAI-specific behavior that is not fully reproduced by OpenClaw.
2. Advanced options copied from upstream may confuse users if OpenClaw ignores them.
3. The phrase "custom API endpoint" sounds simple, but the real compatibility boundary is request semantics, not just URL substitution.
4. Voice and media features may create false expectations if included too early.
5. Repository-level HACS requirements can still fail CI even when the code and checked-in metadata are correct.

## Open Questions

1. Should the initial implementation include only the `conversation` platform, or `conversation` plus `ai_task`?
2. Should the config flow normalize a host URL into a `/v1` API root automatically, or require the full API root explicitly?
3. Should the model field be free-text initially, or should the integration fetch and offer a dropdown from `/v1/models`?
4. Do we want to support custom headers such as `x-openclaw-model` in a later phase?
5. Do we need a user-facing SSL verification option for self-signed deployments, or should that be deferred?
6. Should we track upstream `openai_conversation` periodically and document an update strategy?
7. Which repository topics should be considered the canonical public metadata set for HACS publication?

## Recommended Initial Scope Decision

Proceed with an initial implementation scope of:

- custom integration domain `openclaw_conversation`
- config flow with `base_url` and bearer token
- runtime OpenAI-compatible client using custom base URL
- `conversation` support
- optional `ai_task` support if it shares the same compatible request path cleanly
- HACS-compatible repository metadata and CI

Defer to later specs:

- STT
- TTS
- image generation
- OpenAI-specific advanced tuning controls not confirmed compatible with OpenClaw

