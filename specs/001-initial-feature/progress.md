# Progress

- Spec ID: 001-initial-feature
- Last updated: 2026-03-28
- Status: Drafted

## Completed

1. Confirmed the workspace had no prior local spec template to inherit.
2. Researched the OpenClaw OpenAI-compatible Gateway API.
3. Reviewed the upstream Home Assistant `openai_conversation` integration structure and behavior.
4. Reviewed Home Assistant custom integration manifest guidance.
5. Reviewed HACS custom integration repository requirements and GitHub Action guidance.
6. Drafted the initial feature spec.

## Decisions Made

1. Use `specs/001-initial-feature/` as the numbered Speckit-style folder.
2. Treat the repository target as a **HACS custom integration repository**, not a Supervisor add-on repository.
3. Keep the initial product scope focused on LLM conversation use cases.
4. Defer STT, TTS, and image-generation support until OpenClaw compatibility is verified.
5. Use a configurable OpenAI-compatible `base_url` as the core differentiator from upstream `openai_conversation`.

## Next Steps

1. Confirm whether initial implementation should include `ai_task` alongside `conversation`.
2. Confirm whether the config flow should require a `/v1` URL or normalize host input automatically.
3. Confirm whether model selection should start as free-text or fetched choices from `/v1/models`.
4. Start implementation scaffolding only after the spec is approved.

## Known Open Questions

1. SSL/self-signed certificate handling is still unspecified.
2. OpenClaw compatibility for STT/TTS/images is unverified.
3. Long-term upstream sync strategy with Home Assistant core is still undefined.

## Exit Criteria For This Spec Phase

- `spec.md` reflects the intended initial feature scope.
- research findings are captured in `research.md`.
- unresolved scope decisions are visible before coding begins.
