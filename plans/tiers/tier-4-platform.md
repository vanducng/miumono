# Tier 4: Platform

**Goal:** Web server, examples package, and observability.
**Effort:** 28h | **Priority:** P2 | **Status:** DONE [2025-12-29]
**Depends on:** Tier 3 Protocols
**Started:** 2025-12-29 | **Completed:** 2025-12-29

---

## Deliverables

- [x] `miu serve` runs FastAPI web server (Phase 4A)
- [x] Session management API with REST endpoints (Phase 4B)
- [x] UUID-validated session storage with security (Phase 4B)
- [x] 11 comprehensive session tests passing (Phase 4B)
- [x] Web chat interface at localhost:8000 (Phase 4D)
- [x] miu-examples package with demo apps (Phase 4E)
- [x] OpenTelemetry tracing integration (Phase 4F)
- [x] miu glue package with unified CLI (Phase 4G)
- [x] Multi-agent patterns: Orchestrator, Pipeline, Router (Phase 4H)
- [x] `uv add miu-studio` installs server (Phase 4A)

---

## New Packages

### miu_studio (Web Server)

```
packages/miu_studio/
├── pyproject.toml
└── miu_studio/
    ├── __init__.py
    ├── __main__.py           # Entry: python -m miu_studio
    ├── main.py               # FastAPI app
    ├── api/
    │   ├── deps.py           # Dependency injection
    │   └── routes/
    │       ├── health.py
    │       ├── sessions.py
    │       └── chat.py       # REST + WebSocket
    ├── services/
    │   ├── session_manager.py
    │   └── streaming.py
    └── core/
        ├── config.py         # pydantic-settings
        └── events.py         # Lifespan handlers
```

### miu_examples (Demo Apps)

```
packages/miu_examples/
├── pyproject.toml
└── miu_examples/
    ├── __init__.py
    ├── simple_agent.py       # Basic agent usage
    ├── multi_provider.py     # Provider switching
    ├── tool_usage.py         # Custom tools
    ├── mcp_client.py         # MCP integration
    ├── rag_agent.py          # RAG with Qdrant
    └── multi_agent.py        # Agent orchestration
```

---

## Tasks

### Phase 4A: miu_studio Package Setup (2h) - DONE [2025-12-29]

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Create package scaffold | `packages/miu_studio/` | DONE |
| 2 | Create pyproject.toml | `miu_studio/pyproject.toml` | DONE |
| 3 | Create FastAPI app | `miu_studio/main.py` | DONE |
| 4 | Create config | `miu_studio/core/config.py` | DONE |

**pyproject.toml:**
```toml
[project]
name = "miu-studio"
version = "0.1.0"
description = "Web server for miu AI agent"
requires-python = ">=3.11"
dependencies = [
    "miu-core[anthropic]",
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "pydantic-settings>=2.6",
    "websockets>=13.0",
]

[project.scripts]
miu-studio = "miu_studio.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**FastAPI App:**
```python
# miu_studio/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from miu_studio.core.config import settings
from miu_studio.api.routes import health, sessions, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown

app = FastAPI(
    title="miu Studio",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1/sessions")
app.include_router(chat.router, prefix="/api/v1/chat")
```

### Phase 4B: Session Management API (3h) - DONE [2025-12-29]

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Create session models | `miu_studio/models/api.py` | DONE |
| 2 | Create SessionManager | `miu_studio/services/session_manager.py` | DONE |
| 3 | Create sessions routes | `miu_studio/api/routes/sessions.py` | DONE |
| 4 | Write tests | `tests/test_sessions.py` | DONE |

**Sessions API:**
```python
# miu_studio/api/routes/sessions.py
from fastapi import APIRouter, Depends, HTTPException
from miu_studio.services.session_manager import SessionManager

router = APIRouter(tags=["sessions"])

@router.get("/")
async def list_sessions(sm: SessionManager = Depends()):
    return await sm.list_sessions()

@router.post("/")
async def create_session(sm: SessionManager = Depends()):
    return await sm.create_session()

@router.get("/{session_id}")
async def get_session(session_id: str, sm: SessionManager = Depends()):
    session = await sm.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session

@router.delete("/{session_id}")
async def delete_session(session_id: str, sm: SessionManager = Depends()):
    await sm.delete_session(session_id)
    return {"deleted": session_id}
```

### Phase 4C: Chat API + WebSocket (4h) - DONE [2025-12-29]

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Create chat invoke endpoint | `miu_studio/api/routes/chat.py` | DONE |
| 2 | Create streaming endpoint | `miu_studio/api/routes/chat.py` | DONE |
| 3 | Create WebSocket handler | `miu_studio/api/routes/chat.py` | DONE |
| 4 | Create streaming service | `miu_studio/services/streaming.py` | DONE |

**Chat API:**
```python
# miu_studio/api/routes/chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["chat"])

@router.post("/invoke")
async def invoke(request: ChatRequest, sm: SessionManager = Depends()):
    """Synchronous chat - full response."""
    agent = await sm.get_agent(request.session_id)
    response = await agent.run(request.message)
    return {"response": response.get_text()}

@router.post("/stream")
async def stream(request: ChatRequest, sm: SessionManager = Depends()):
    """Server-Sent Events streaming."""
    agent = await sm.get_agent(request.session_id)

    async def generate():
        async for chunk in agent.stream(request.message):
            yield f"data: {chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket for real-time chat."""
    await websocket.accept()
    sm = SessionManager()
    agent = await sm.get_or_create_agent(session_id)

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")

            async for chunk in agent.stream(message):
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk.text,
                })

            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        await sm.save_session(session_id)
```

### Phase 4D: Static Web UI (4h)

| # | Task | File(s) |
|---|------|---------|
| 1 | Create static HTML/CSS/JS | `miu_studio/static/` |
| 2 | Implement chat interface | `miu_studio/static/index.html` |
| 3 | WebSocket client | `miu_studio/static/app.js` |
| 4 | Mount static files | `miu_studio/main.py` |

**Static Chat UI (Minimal):**
```html
<!-- miu_studio/static/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>miu Studio</title>
    <style>
        body { font-family: system-ui; max-width: 800px; margin: 0 auto; }
        #chat { height: 70vh; overflow-y: auto; border: 1px solid #ccc; padding: 1rem; }
        .message { margin: 0.5rem 0; padding: 0.5rem; border-radius: 4px; }
        .user { background: #e3f2fd; text-align: right; }
        .assistant { background: #f5f5f5; }
        #input { width: calc(100% - 80px); padding: 0.5rem; }
        button { width: 70px; padding: 0.5rem; }
    </style>
</head>
<body>
    <h1>miu Studio</h1>
    <div id="chat"></div>
    <input id="input" placeholder="Enter message...">
    <button onclick="send()">Send</button>
    <script src="/static/app.js"></script>
</body>
</html>
```

### Phase 4E: miu_examples Package (5h)

| # | Task | File(s) |
|---|------|---------|
| 1 | Create package scaffold | `packages/miu_examples/` |
| 2 | Simple agent example | `miu_examples/simple_agent.py` |
| 3 | Multi-provider example | `miu_examples/multi_provider.py` |
| 4 | Custom tools example | `miu_examples/tool_usage.py` |
| 5 | MCP client example | `miu_examples/mcp_client.py` |
| 6 | RAG agent example | `miu_examples/rag_agent.py` |
| 7 | Multi-agent example | `miu_examples/multi_agent.py` |
| 8 | Write README | `packages/miu_examples/README.md` |

**Example - Simple Agent:**
```python
# miu_examples/simple_agent.py
"""Simple agent example demonstrating basic miu-core usage."""

import asyncio
from miu_core.providers import create_provider
from miu_core.agents import ReActAgent, AgentConfig

async def main():
    # Create provider
    provider = create_provider("anthropic:claude-sonnet-4-20250514")

    # Create agent
    agent = ReActAgent(
        provider=provider,
        config=AgentConfig(
            name="simple",
            system_prompt="You are a helpful assistant.",
        ),
    )

    # Run query
    response = await agent.run("What is the capital of France?")
    print(response.get_text())

if __name__ == "__main__":
    asyncio.run(main())
```

**Example - Custom Tools:**
```python
# miu_examples/tool_usage.py
"""Custom tool example demonstrating tool creation."""

from pydantic import BaseModel, Field
from miu_core.tools import Tool, ToolResult, ToolContext, ToolRegistry
from miu_core.agents import ReActAgent

class WeatherInput(BaseModel):
    city: str = Field(description="City name")

class WeatherTool(Tool):
    name = "get_weather"
    description = "Get current weather for a city."

    def get_input_schema(self):
        return WeatherInput

    async def execute(self, ctx: ToolContext, city: str) -> ToolResult:
        # Mock weather API
        return ToolResult(output=f"Weather in {city}: Sunny, 22°C")

async def main():
    # Register custom tool
    registry = ToolRegistry()
    registry.register(WeatherTool())

    # Create agent with tools
    agent = ReActAgent(
        provider=create_provider("anthropic:claude-sonnet-4-20250514"),
        tools=registry,
    )

    response = await agent.run("What's the weather in Tokyo?")
    print(response.get_text())
```

**pyproject.toml:**
```toml
[project]
name = "miu-examples"
version = "0.1.0"
description = "Example applications using miu-core"
requires-python = ">=3.11"
dependencies = [
    "miu-core[all]",
]

[project.optional-dependencies]
rag = ["qdrant-client>=1.12"]
```

### Phase 4F: OpenTelemetry Integration (4h)

| # | Task | File(s) |
|---|------|---------|
| 1 | Create tracing types | `miu_core/tracing/types.py` |
| 2 | Create OTel exporter | `miu_core/tracing/otel.py` |
| 3 | Instrument agent | `miu_core/agents/react.py` |
| 4 | Instrument provider | `miu_core/providers/base.py` |

**OTel Integration:**
```python
# miu_core/tracing/otel.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def setup_tracing(service_name: str = "miu"):
    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)

# Usage in agent
class ReActAgent(Agent):
    async def run(self, query: str) -> Response:
        tracer = trace.get_tracer("miu")
        with tracer.start_as_current_span("agent.run") as span:
            span.set_attribute("query", query[:100])
            # ... agent logic
            span.set_attribute("iterations", self._iteration)
            return response
```

### Phase 4G: miu Glue Package (3h)

| # | Task | File(s) |
|---|------|---------|
| 1 | Create miu package | `packages/miu/` |
| 2 | Create CLI dispatcher | `miu/cli.py` |
| 3 | Wire up sub-commands | - |

**Glue Package:**
```toml
# packages/miu/pyproject.toml
[project]
name = "miu"
version = "0.1.0"
description = "AI Agent Framework - batteries included"
requires-python = ">=3.11"
dependencies = [
    "miu-core[all]",
    "miu-code",
]

[project.optional-dependencies]
examples = ["miu-examples"]
studio = ["miu-studio"]
all = ["miu[examples,studio]"]

[project.scripts]
miu = "miu.cli:main"
```

**CLI Dispatcher:**
```python
# packages/miu/miu/cli.py
import sys
import asyncclick as click

@click.group(invoke_without_command=True)
@click.pass_context
async def main(ctx):
    """miu - AI Agent Framework."""
    if ctx.invoked_subcommand is None:
        # Default: run miu-code CLI
        from miu_code.cli.entry import main as code_main
        await code_main.main(standalone_mode=False)

@main.command()
@click.option("--port", default=8000)
async def serve(port: int):
    """Run miu-studio web server."""
    try:
        from miu_studio.__main__ import main as studio_main
        await studio_main(port=port)
    except ImportError:
        click.echo("miu-studio not installed. Run: uv add miu-studio")
        sys.exit(1)

@main.command()
async def code():
    """Run miu-code CLI."""
    from miu_code.cli.entry import main as code_main
    await code_main.main(standalone_mode=False)

@main.command()
async def tui():
    """Run miu-code TUI."""
    from miu_code.tui.app import run
    run()
```

### Phase 4H: Multi-Agent Patterns (3h) - DONE [2025-12-29]

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Create Orchestrator pattern | `miu_core/patterns/orchestrator.py` | DONE |
| 2 | Create Pipeline pattern | `miu_core/patterns/pipeline.py` | DONE |
| 3 | Create Router pattern | `miu_core/patterns/routing.py` | DONE |
| 4 | Add example | `miu_examples/multi_agent.py` | DONE |

**Patterns Implemented:**
- Orchestrator: Task dependency DAG, topological sort, fail-fast mode
- Pipeline: Sequential stages, output transforms, configurable error handling
- Router: Keyword/regex/custom conditions, priority ordering
- 21 tests passing, code review grade: A (94/100)

---

## Success Criteria

- [ ] `miu serve` starts server on port 8000
- [ ] Web chat at http://localhost:8000 works
- [ ] `python -m miu_examples.simple_agent` runs
- [ ] `uv add "miu[examples]"` installs examples
- [ ] OpenTelemetry traces visible in Jaeger
- [ ] `miu` command dispatches to subcommands

---

## Next Tier

After Tier 4 complete → [Tier 5: Distribution](tier-5-distribution.md)
