---
name: SKILL_NAME
description: WHAT it does, in one sentence. Use this whenever <the situations, phrasings and file types that should trigger it, including ones where the user doesn't name it>. Also use it when <adjacent cases it should win>. Be specific and a little pushy; this text is what makes Claude pick the skill.
---

# SKILL_TITLE

One paragraph: what this skill does and which bundled script or reference does the heavy lifting. Tell Claude to run the bundled scripts rather than rewrite them.

## Before acting

Any confirmation or safety check the user should see first, and why. For example: publishing, spending quota, or touching data outside the repo.

## Workflow

1. Step, with the exact command, for example `python3 scripts/<tool>.py --dry-run …`
2. Step
3. How to verify the result and what to report back.

## Gotchas (observed)

Things learned the hard way, each with the reason, so future runs don't rediscover them.
