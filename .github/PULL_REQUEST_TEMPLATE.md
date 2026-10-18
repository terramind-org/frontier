<!-- Prefer `bun frontier submit <attempt-dir>`: it generates this text for you. -->
<!-- A PR adds exactly one new attempts/<problem>/<attempt>/ directory and nothing else. -->

## Attempt: <problem title>

- **Problem:** `<problem-id>` ([problem file](https://github.com/terramind-org/frontier/blob/HEAD/problems/<problem-id>.yaml))
- **Attempt:** `<attempt-id>`
- **Kind:** proof | disproof | witness | writeup
- **Mode:** ai_only | human_ai | human_only
- **Local verdict:** <output of `bun frontier check <attempt-dir>`, or "no local verdict; CI will check">. CI re-checks every attempt; the verdict recorded on `main` is the one that counts.

### Claim

<what this attempt claims, exactly, in your words>

### Models and tools

- <model (provider): role>

### People

- <name (@github): role>

### Declarations

- [ ] I have the right to submit this work, and I submit it under CC BY 4.0.
- [ ] The models, tools and people listed above are the complete disclosure of how this was produced.
