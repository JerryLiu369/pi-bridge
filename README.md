# pi-bridge

Python wrapper for the [Pi Agent SDK](https://github.com/earendil-works/pi). Lets you drive a Pi coding agent from Python via a local Node.js bridge process.

## Dependencies

- **Node.js** ≥ 18
- **Pi Agent** installed globally:
  ```bash
  npm install -g @earendil-works/pi-coding-agent
  ```
- **Python** ≥ 3.11

## Installation

```bash
git clone <this-repo>
cd pi-bridge
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```python
from pi_bridge import PiSession, Provider, Model

session = PiSession(
    provider=Provider(
        base_url="https://api.deepseek.com/v1",
        api_key="sk-...",
    ),
    model=Model(
        name="deepseek-chat",
        api_format="completion",  # "completion" | "response" | "anthropic"
    ),
    cwd="/your/project",          # working directory for the agent
)

# Send a message and get all events at once
events = session.send("列出当前目录的文件")
for e in events:
    if e.type == "text_delta":
        print(e.delta, end="", flush=True)

# Or stream events one by one
for e in session.send_stream("解释一下 main.py"):
    if e.type == "text_delta":
        print(e.delta, end="", flush=True)

session.close()
```

Multiple `send()` calls on the same session share context — the agent remembers the full conversation history automatically.

## Custom tools

```python
from pi_bridge import PiSession, Provider, Model, CustomTool

def web_search(query: str) -> str:
    return "..."  # your implementation

session = PiSession(
    provider=Provider(...),
    model=Model(...),
    custom_tools=[
        CustomTool(
            name="web_search",
            description="Search the web",
            parameters={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            fn=web_search,
        )
    ],
)
```

## API reference

### `PiSession`

| Parameter | Type | Description |
|-----------|------|-------------|
| `provider` | `Provider` | API endpoint and key |
| `model` | `Model` | Model name and format |
| `cwd` | `str` | Agent working directory (default: `.`) |
| `system_prompt` | `str` | Override system prompt |
| `tools` | `list[str] \| None` | Built-in tool allowlist; `None` = all defaults, `[]` = none |
| `custom_tools` | `list[CustomTool]` | Python-side tools |
| `persist` | `bool` | Persist session to disk (default: `False`) |

| Method | Description |
|--------|-------------|
| `send(msg)` | Send message, block until done, return all events |
| `send_stream(msg)` | Send message, yield events as they arrive |
| `messages` | Full conversation history |
| `state` | Current session state (model, message count, …) |
| `set_model(provider, model)` | Switch model at runtime |
| `set_thinking_level(level)` | Set thinking level: `off` / `minimal` / `low` / `medium` / `high` / `xhigh` |
| `compact(instructions)` | Manually trigger context compaction |
| `abort()` | Abort current operation |
| `close()` | Shut down the bridge process |

### `Model.api_format`

| Value | Provider |
|-------|----------|
| `"anthropic"` | Anthropic Claude |
| `"completion"` | OpenAI Chat Completions, DeepSeek, Groq, … |
| `"response"` | OpenAI Responses API |
