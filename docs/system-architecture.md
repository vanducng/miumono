# System Architecture

**Project:** Miumono - AI Agent Framework
**Version:** 0.1.0
**Last Updated:** 2025-12-29

## Architecture Overview

Miumono follows a layered, modular architecture with clear separation of concerns spanning CLI and web interfaces:

```
┌─────────────────────────────────────┐  ┌─────────────────────────────────────┐
│       CLI Layer (miu-code)          │  │     Web Layer (miu-studio)          │
│   ┌─────────────┬──────────┐        │  │   ┌────────────┬──────────────┐     │
│   │   Entry     │  REPL    │        │  │   │  Static UI │  REST API    │     │
│   │   Point     │  Mode    │        │  │   │  Assets    │  Endpoints   │     │
│   └──────┬──────┴────┬─────┘        │  │   └──────┬──────┴──────┬───────┘     │
└──────────┼───────────┼───────────────┘  └─────────┼───────────┼──────────────┘
           │           │                            │           │
┌──────────▼───────────▼─────────────────────────────▼───────────▼──────────────┐
│                    Agent & Orchestration Layer                                 │
│   ┌────────────────────────────────────┐      ┌─────────────────────────┐    │
│   │    Coding Agent (ReAct Pattern)    │      │   WebSocket Handler     │    │
│   │  • Tool Selection & Execution      │      │  • Real-time sessions   │    │
│   │  • Message routing                 │      │  • Event broadcasting   │    │
│   │  • Reasoning Loop                  │      │                         │    │
│   └─────────┬──────────────────────────┘      └────────────┬────────────┘    │
└─────────────┼──────────────────────────────────────────────┼──────────────────┘
              │                                               │
┌─────────────▼───────────────────────────────────────────────▼──────────────────┐
│                     Framework Layer (miu-core)                                  │
│  ┌──────────────┬────────────┬──────────────┬──────────────────────┐           │
│  │   Agents     │    Tools   │   Models     │    Configuration     │           │
│  │              │            │              │    & Settings        │           │
│  │ • BaseAgent  │ • Registry │ • Message    │ • Environment vars   │           │
│  │ • ReActAgent │ • Executor │ • Tool       │ • App settings       │           │
│  │              │            │ • Response   │ • Session management │           │
│  └──────────────┴────────────┴──────────────┴──────────────────────┘           │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │              Provider Interface (Abstraction for LLM backends)             │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
└────────┬──────────────┬──────────────────────────────────┬───────────────────┘
         │              │                                  │
┌────────▼──┐   ┌───────▼───┐   ┌──────────────────────────▼──┐
│ Anthropic │   │   OpenAI   │   │       Google Gemini         │
│  Claude   │   │            │   │                             │
└───────────┘   └────────────┘   └─────────────────────────────┘
```

## Core Components

### 1. Framework Layer (miu-core)

#### Agent Framework

**Location:** `packages/miu_core/miu_core/agents/`

**Components:**

- **BaseAgent:** Abstract base class defining agent interface
  - `run(query)`: Main entry point
  - `_execute_step()`: Single reasoning step
  - Tool registry access
  - Message history management

- **ReActAgent:** Concrete implementation
  - Implements ReAct (Reasoning + Acting) pattern
  - Iterative tool selection and execution
  - Graceful error handling and recovery
  - Message history tracking

**Key Methods:**
```python
class BaseAgent:
    async def run(self, query: str) -> str:
        """Run agent with given query."""

    async def _execute_step(self, context: AgentContext) -> bool:
        """Execute single step, return True if done."""

    def _get_tools_prompt(self) -> str:
        """Get formatted list of available tools."""
```

#### Tool System

**Location:** `packages/miu_core/miu_core/tools/`

**Components:**

- **BaseTool:** Abstract tool interface
  - `name`: Tool identifier
  - `description`: Human-readable description
  - `parameters`: JSON schema of tool parameters
  - `execute()`: Async execution method

- **ToolRegistry:** Central tool management
  - Tool registration
  - Tool lookup by name
  - Tool execution with validation
  - Tool discovery and listing

**Tool Architecture:**
```python
class BaseTool(ABC):
    name: str
    description: str
    parameters: dict[str, Any]

    async def execute(self, **kwargs) -> ToolResult:
        """Execute tool with validated parameters."""

class ToolRegistry:
    def register(self, tool: BaseTool) -> None:
        """Register a tool."""

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Execute tool by name."""
```

#### Provider Interface

**Location:** `packages/miu_core/miu_core/providers/`

**Components:**

- **BaseProvider:** Provider abstraction
  - Unified interface across LLM providers
  - `generate()`: Request completion from LLM
  - Tool/function calling support
  - Token usage tracking

- **AnthropicProvider:** Anthropic Claude implementation
- **OpenAIProvider:** OpenAI GPT implementation
- **GoogleProvider:** Google Gemini implementation

**Provider Interface:**
```python
class BaseProvider(ABC):
    async def generate(
        self,
        messages: list[Message],
        tools: Optional[list[Tool]] = None,
        max_tokens: int = 2048,
    ) -> GenerateResponse:
        """Generate response from LLM."""

    def _format_tools(self, tools: list[Tool]) -> Any:
        """Format tools for provider's API."""

    def _parse_response(self, response: Any) -> GenerateResponse:
        """Parse provider response."""
```

#### Data Models

**Location:** `packages/miu_core/miu_core/models/`

**Key Models:**

- **Message:** Represents conversation message
  - `role`: "user", "assistant", "tool"
  - `content`: Message content
  - `tool_call`: Optional tool call info

- **Tool:** Tool definition
  - `name`: Tool identifier
  - `description`: Tool purpose
  - `parameters`: JSON schema

- **ToolResult:** Tool execution result
  - `output`: Tool output
  - `error`: Optional error message
  - `metadata`: Additional info

- **Response:** LLM response
  - `content`: Text content
  - `tool_calls`: List of tool calls
  - `stop_reason`: Why response ended

### 2. Coding Agent Layer (miu-code)

**Location:** `packages/miu_code/miu_code/agent/`

**CodingAgent:** Specialization of ReActAgent

- Customized tool set for code operations
- Enhanced error handling for file operations
- Code-specific reasoning prompts
- Session-aware state management

**Implementation Pattern:**
```python
class CodingAgent(ReActAgent):
    """Agent specialized for code operations."""

    def __init__(self, provider: BaseProvider) -> None:
        super().__init__(provider)
        self._setup_coding_tools()

    def _setup_coding_tools(self) -> None:
        """Register code-specific tools."""
        self.tool_registry.register(ReadFileTool())
        self.tool_registry.register(WriteFileTool())
        self.tool_registry.register(EditFileTool())
        self.tool_registry.register(BashTool())
        self.tool_registry.register(GlobTool())
        self.tool_registry.register(GrepTool())
```

### 3. Tool Implementations (miu-code)

**Location:** `packages/miu_code/miu_code/tools/`

**Implemented Tools:**

| Tool | Purpose | Parameters |
|------|---------|-----------|
| `read` | Read file contents | path: str |
| `write` | Write new file | path: str, content: str |
| `edit` | Modify existing file | path: str, old: str, new: str |
| `bash` | Execute shell command | command: str |
| `glob` | Find files by pattern | pattern: str |
| `grep` | Search file contents | pattern: str, path: str |

**Tool Base:**
```python
class FileTool(BaseTool):
    """Base class for file operations."""

    async def execute(self, **kwargs) -> ToolResult:
        """Execute with path validation."""
        path = self._validate_path(kwargs["path"])
        return await self._do_execute(path, **kwargs)

    def _validate_path(self, path: str) -> Path:
        """Validate and resolve path safely."""
        # Prevent directory traversal attacks
        # Ensure path is within allowed boundaries
```

### 4. Web Server Layer (miu-studio)

**Location:** `packages/miu_studio/`

**Components:**

- **FastAPI Application:** Async web framework for REST API
  - `create_app()`: Factory function for app initialization
  - Automatic OpenAPI documentation
  - Request/response validation via Pydantic
  - Built-in CORS middleware

- **Configuration Management:** Pydantic Settings
  - Environment variable loading (`MIU_*` prefix)
  - Type-safe settings access
  - Server, agent, session, and logging configuration

- **API Routes:** RESTful endpoints
  - Health check endpoints (`/api/v1/health`, `/api/v1/ready`)
  - Future: Agent operations, session management, streaming

- **Static File Serving:** Web UI assets
  - Mounted at `/static`
  - Serves HTML, JS, CSS for web interface

- **CORS Middleware:** Cross-origin resource sharing
  - Configurable origins (default: `["*"]`)
  - Credentials support for auth

**Application Factory Pattern:**
```python
def create_app() -> FastAPI:
    """Initialize FastAPI app with all components."""
    app = FastAPI(...)
    app.add_middleware(CORSMiddleware, ...)
    app.include_router(health.router, prefix="/api/v1")
    # Mount static files if exists
    return app
```

**Server Configuration:**
```python
class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Agent defaults
    default_model: str = "claude-sonnet-4-20250514"
    default_provider: str = "anthropic"

    # Session management
    session_dir: str = ".miu/sessions"
    session_timeout: int = 3600
```

### 5. CLI Layer (miu-code)

**Location:** `packages/miu_code/miu_code/cli/`

**Components:**

- **Entry Point:** `miu` command
  - One-shot mode: `miu -q "query"` or `miu --query "query"`
  - Interactive REPL mode: `miu` (launches interactive prompt)
  - Interactive TUI mode: `miu code` (launches graphical interface)
  - Option parsing and validation

- **REPL Mode:** Interactive prompt
  - Command history
  - Auto-completion
  - Session persistence
  - Syntax highlighting

**CLI Flow:**
```
User Input
    │
    ▼
Command Parser
    │
    ├─ One-shot: Execute → Output → Exit
    │
    └─ Interactive: REPL Loop
        ├─ Prompt
        ├─ Parse
        ├─ Execute
        ├─ Display
        └─ Loop
```

### 6. Session Management (miu-code)

**Location:** `packages/miu_code/miu_code/session/`

**Features:**

- Session storage and retrieval
- Conversation history persistence
- Context management across sessions
- Session cleanup and expiry

## Data Flow Patterns

### Agent Execution Flow

```
User Query
    │
    ▼
Agent.run(query)
    │
    ├─ Create initial message
    ├─ Add to message history
    │
    ├─ Loop:
    │   ├─ Get provider response
    │   │   └─ Format messages + tools
    │   │   └─ Call LLM API
    │   │   └─ Parse response
    │   │
    │   ├─ Check for tool calls
    │   │
    │   ├─ If tool call:
    │   │   ├─ Validate tool & args
    │   │   ├─ Execute tool
    │   │   ├─ Add result to history
    │   │   └─ Continue loop
    │   │
    │   └─ Else: Return final response
    │
    ▼
Agent Response
```

### Tool Execution Flow

```
Tool Call
    │
    ├─ Validate tool name exists
    │
    ├─ Parse arguments
    ├─ Validate against schema
    │
    ├─ Execute tool
    │   ├─ Input validation
    │   ├─ Safety checks
    │   ├─ Perform operation
    │   └─ Capture result
    │
    ├─ Handle errors
    │   └─ Include in result
    │
    ▼
ToolResult
```

### Provider Abstraction

```
Agent
    │
    ├─ Call provider.generate()
    │
Provider (Implementation)
    │
    ├─ Format request for API
    ├─ Call provider API
    ├─ Handle rate limits/errors
    ├─ Parse response
    ├─ Extract tool calls
    │
    ▼
Normalized Response
```

## Key Abstractions

### Provider Abstraction

**Why:** Allow swapping LLM providers without agent changes

**How:** Common interface with provider-specific implementations

```python
# Agent code is provider-agnostic
response = await self.provider.generate(messages, tools)

# Provider implementation varies
class AnthropicProvider(BaseProvider):
    async def generate(...):
        # Use Anthropic SDK
        return anthropic_client.messages.create(...)

class OpenAIProvider(BaseProvider):
    async def generate(...):
        # Use OpenAI SDK
        return openai_client.chat.completions.create(...)
```

### Tool Registry Pattern

**Why:** Decouple tool definition from agent

**How:** Central registry for tool discovery and execution

```python
# Register once
registry.register(ReadFileTool())

# Agent discovers and uses
tools = registry.get_available_tools()
result = await registry.execute("read", {"path": "file.py"})
```

## Async Architecture

### Concurrency Model

- **Event Loop:** Single asyncio event loop
- **Concurrency:** gather() for parallel operations
- **I/O:** All blocking operations are async (files, HTTP, subprocess)
- **Timeouts:** All external calls have timeouts

### Async Patterns

**File Operations:**
```python
# Async file I/O using aiofiles
async with aiofiles.open(path, "r") as f:
    content = await f.read()
```

**HTTP Requests:**
```python
# Async HTTP using httpx
async with httpx.AsyncClient() as client:
    response = await client.get(url, timeout=30)
```

**Concurrent Operations:**
```python
# Execute multiple tools in parallel
results = await asyncio.gather(
    execute_tool1(),
    execute_tool2(),
    execute_tool3(),
)
```

## Error Handling Strategy

### Error Hierarchy

```
MiuError (base)
├── ProviderError
│   ├── ProviderAPIError
│   ├── ProviderTimeoutError
│   └── ProviderRateLimitError
├── ToolError
│   ├── ToolNotFoundError
│   ├── ToolExecutionError
│   └── ToolValidationError
└── AgentError
    ├── AgentInitializationError
    └── AgentExecutionError
```

### Error Handling Patterns

**Graceful Degradation:**
```python
async def execute_tool_safely(tool: Tool) -> ToolResult:
    try:
        return await tool.execute()
    except ToolError as e:
        logger.error(f"Tool failed: {e}")
        return ToolResult(error=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return ToolResult(error="Tool execution failed unexpectedly")
```

## Security Architecture

### Input Validation

- **Path Validation:** Prevent directory traversal attacks
- **Command Validation:** Escape shell commands properly
- **API Keys:** Load from environment variables only
- **Rate Limiting:** Prevent abuse of tool/API usage

### Security Layers

```
┌─────────────────────────────────┐
│    User Input (Query)            │
├─────────────────────────────────┤
│    Input Validation              │
├─────────────────────────────────┤
│    Tool Execution Layer          │
│    • Path validation             │
│    • Command escaping            │
│    • Result validation           │
├─────────────────────────────────┤
│    Provider Layer                │
│    • API key validation          │
│    • Request validation          │
│    • Rate limiting               │
├─────────────────────────────────┤
│    External Services (APIs)      │
└─────────────────────────────────┘
```

## Extensibility Points

### Adding New Provider

1. Extend `BaseProvider`
2. Implement `generate()` method
3. Implement response parsing
4. Register in provider factory

```python
class CustomProvider(BaseProvider):
    async def generate(self, messages, tools):
        # Implementation
        pass
```

### Adding New Tool

1. Extend `BaseTool`
2. Define `name`, `description`, `parameters`
3. Implement `execute()` method
4. Register in tool registry

```python
class CustomTool(BaseTool):
    name = "custom"
    description = "Custom tool"

    async def execute(self, **kwargs):
        # Implementation
        pass
```

### Custom Agent Implementation

1. Extend `ReActAgent` or `BaseAgent`
2. Override `_setup_tools()` for tool customization
3. Override `_get_reasoning_prompt()` for custom prompts
4. Override `_execute_step()` for custom logic

### Multi-Agent Patterns

**Location:** `packages/miu_core/miu_core/patterns/`

Three coordination patterns for multi-agent systems:

| Pattern | Purpose | Key Features |
|---------|---------|--------------|
| **Orchestrator** | Coordinate agents with dependencies | Task DAG, topological sort, fail-fast |
| **Pipeline** | Sequential processing chain | Stage transforms, error handling |
| **Router** | Route requests to specialists | Keywords, regex, priority ordering |

```python
# Orchestrator - task dependencies
orchestrator = Orchestrator()
orchestrator.add_agent("research", research_agent)
orchestrator.add_task("task1", "research", "query", depends_on=["task0"])
results = await orchestrator.run()

# Pipeline - sequential stages
pipeline = Pipeline()
pipeline.add_stage("extract", agent1)
pipeline.add_stage("transform", agent2, transform=lambda q, r: f"Process: {r.get_text()}")
result = await pipeline.run("initial query")

# Router - request routing
router = Router()
router.add_route("code", code_agent, keywords=["python", "debug"])
router.add_route("general", general_agent, condition=lambda q: True, priority=-1)
result = await router.route("Help with Python")
```

## Dependency Management

### Internal Dependencies

```
miu-code
    └── miu-core[anthropic]
        ├── pydantic
        ├── httpx
        ├── aiofiles
        ├── packaging
        └── anthropic (optional)
```

### Dependency Isolation

- **miu-core:** No CLI dependencies (pure framework)
- **miu-code:** CLI dependencies isolated to UI layer
- **Providers:** Optional dependencies - fail gracefully if missing

## Performance Considerations

### Scalability

- **Async I/O:** Non-blocking file and network operations
- **Concurrent Execution:** Multiple tools run in parallel
- **Lazy Loading:** Providers loaded only when needed
- **Caching:** Session caching for repeated operations

### Memory Management

- **Message History:** Keep bounded history size
- **Streaming:** Stream large file operations
- **Cleanup:** Explicit cleanup of resources

## Testing Architecture

### Test Structure

```
miu_core/
├── tests/
│   ├── test_core_models.py
│   ├── test_core_tools.py
│   └── test_providers.py

miu_code/
├── tests/
│   ├── test_code_tools.py
│   └── test_agent.py
```

### Testing Levels

- **Unit Tests:** Individual classes and functions
- **Integration Tests:** Component interactions
- **E2E Tests:** Full agent execution flow

---

**Architecture Version:** 1.0
**Last Updated:** 2025-12-29
**Maintainers:** Development Team
