# ALF 2.4 Install Skill

This repository packages the `install-alf-24` workflow for both Codex-compatible agents and other AI agents.

The workflow installs ALF 2.4 and pyALF from the `ALF-2.4` branches, prepares a conda environment named `ALFDQMC` or a non-conflicting fallback name, and runs the pyALF notebooks as the final installation check.

## Repository Layout

```text
skills/
  install-alf-24/
    SKILL.md
    agents/openai.yaml
    references/alf24-requirements.md
    scripts/prepare_alf24.py
PORTABLE_AGENT_INSTRUCTIONS.md
agent-package.json
```

## Codex-Compatible Install

Use the OpenAI/Codex skill folder directly:

```bash
python /path/to/skill-installer/scripts/install-skill-from-github.py \
  --repo YOUR_GITHUB_USERNAME/alf-2.4-install-skill \
  --path skills/install-alf-24
```

Or install from the GitHub URL:

```bash
python /path/to/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/YOUR_GITHUB_USERNAME/alf-2.4-install-skill/tree/main/skills/install-alf-24
```

Restart Codex after installation so the skill is discovered.

## Non-Codex Agent Install

For agents that do not support OpenAI-style `SKILL.md` skills:

1. Clone or download this repository.
2. Add `PORTABLE_AGENT_INSTRUCTIONS.md` to the agent's custom instructions, tool instructions, project knowledge, or equivalent context store.
3. Make the repository files available to the agent, especially `skills/install-alf-24/scripts/prepare_alf24.py`.
4. Ask the agent to follow `PORTABLE_AGENT_INSTRUCTIONS.md` when installing ALF 2.4.

If an agent cannot execute local shell commands, the user can still run the helper script manually after reading the portable instructions.

## Direct Manual Run

From this repository:

```bash
python skills/install-alf-24/scripts/prepare_alf24.py --install-dir /path/without/spaces --env-base ALFDQMC
```

Use a real install path with no spaces. On Windows, run from inside WSL rather than native PowerShell or cmd.

## Validation

Validate the Codex skill folder with:

```bash
python /path/to/skill-creator/scripts/quick_validate.py skills/install-alf-24
```

## License

MIT License. See `LICENSE`.
