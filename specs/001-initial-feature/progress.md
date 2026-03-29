# Progress

- Spec ID: 001-initial-feature
- Last updated: 2026-03-28
- Status: Implemented (initial scaffold)

## Completed

1. Confirmed the workspace had no prior local spec template to inherit.
2. Researched the OpenClaw OpenAI-compatible Gateway API.
3. Reviewed the upstream Home Assistant `openai_conversation` integration structure and behavior.
4. Reviewed Home Assistant custom integration manifest guidance.
5. Reviewed HACS custom integration repository requirements and GitHub Action guidance.
6. Drafted the initial feature spec.
7. Implemented the initial custom integration scaffold under `custom_components/openclaw_conversation/`.
8. Added repository metadata for HACS and contributor workflows.
9. Added GitHub Actions for HACS validation, hassfest, and Ruff linting.

## Decisions Made

1. Use `specs/001-initial-feature/` as the numbered Speckit-style folder.
2. Treat the repository target as a **HACS custom integration repository**, not a Supervisor add-on repository.
3. Keep the initial product scope focused on LLM conversation use cases.
4. Defer STT, TTS, and image-generation support until OpenClaw compatibility is verified.
5. Use a configurable OpenAI-compatible `base_url` as the core differentiator from upstream `openai_conversation`.
6. Use the OpenAI-compatible Chat Completions API first to keep the initial implementation smaller and easier to validate.
7. Ship one config entry that exposes one conversation entity and one AI Task entity, with advanced model settings managed through options.

## Next Steps

1. Add brand assets so HACS validation no longer needs the current `brands` ignore in CI.
2. Decide whether to fetch model choices dynamically in the config/options flow instead of keeping model entry as free text.
3. Evaluate whether to add OpenAI Responses API support after OpenClaw compatibility is confirmed.
4. Add integration tests once a Home Assistant custom-component test harness is introduced.

## Known Open Questions

1. SSL/self-signed certificate handling is still unspecified.
2. OpenClaw compatibility for STT/TTS/images is unverified.
3. Long-term upstream sync strategy with Home Assistant core is still undefined.
4. Brand asset strategy for public HACS publication is still unfinished.

## Exit Criteria For This Spec Phase

- `spec.md` reflects the intended initial feature scope.
- research findings are captured in `research.md`.
- unresolved scope decisions are visible before coding begins.

## Implementation Outcome

- A HACS-compatible repository scaffold now exists.
- The custom integration includes config flow, options flow, conversation support, and AI Task support.
- Basic repository automation is present for validation and linting.
