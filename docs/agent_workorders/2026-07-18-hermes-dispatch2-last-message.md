Hermes resolved successfully:

```text
/home/manstein/.local/bin/hermes
Hermes Agent v0.18.2 (2026.7.7.2)
Project: /home/manstein/hermes-remote/hermes-agent/venv/lib/python3.11/site-packages
Python: 3.11.15
OpenAI SDK: 2.24.0
Up to date
```

The harvest did **not** run to completion. It exited immediately with this exact error:

```text
usage: hermes [-h] [--version] [-z PROMPT] [--usage-file PATH] [-m MODEL]
...
hermes: error: argument command: invalid choice: 'Hermes' (choose from 'chat', 'model', 'moa', 'fallback', ...)
```

Hermes final summary: **none produced**, because the CLI failed before starting the agent run.

Manifest retrieval output:

```text
===MANIFEST===
===LISTING===
```

Verified PDF count in `~/ssc-pdf-harvest/`: **0**. Explicit check returned:

```text
DIR_MISSING
```

No files in the local repo were modified by me.

