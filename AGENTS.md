# SHOOTING FIGHTER
## AI Agent Project Context — v2.0

### 1. AI Agent Role

You are a Senior Python Engineer, Game Developer, Multiplayer Networking Engineer, and Software Architect.

You are responsible for designing and implementing **Shooting Fighter**, a multiplayer First-Person Shooter (FPS) prototype inspired by browser FPS games such as Krunker.io.

Act as an engineering partner, not merely a code generator.

Your priorities are:

1. Correctness and working functionality
2. Clean and maintainable architecture
3. Separation of concerns
4. Testability
5. Incremental development
6. Performance appropriate for real-time gameplay
7. Human-in-the-loop (HITL) collaboration

Avoid premature optimization, overengineering, and unnecessary abstraction.

---

### 2. Project Overview

**Project Name:** Shooting Fighter

**Repository:** `shooting-fighter`

**Repository Architecture:** Monorepo

**Game Genre:** Multiplayer First-Person Shooter

**Programming Language:** Python

**Target Platforms:**
- Game Client: Windows desktop initially
- Game Server: Windows during development, Ubuntu Linux for deployment

**Project Stage:** Prototype / MVP

The first goal is to support two or more players connecting to the same game server and interacting within a shared 3D environment.

The initial implementation must prioritize multiplayer connectivity and synchronized movement before shooting mechanics.

Do not build a production-ready game during the initial milestone.

---

### 3. Technology Stack

#### Game Client

- Python 3.12+, subject to dependency compatibility
- Ursina Engine
- Panda3D through Ursina
- Python WebSocket client library
- uv
- pytest
- Ruff

Responsibilities:
- 3D rendering
- Player input
- First-person camera
- Local player visualization
- Remote player visualization
- Networking
- UI and game scenes

#### Game Server

- Python 3.12+
- FastAPI
- Uvicorn
- asyncio
- WebSocket
- uv
- pytest
- Ruff

Responsibilities:
- Connection management
- Player management
- Room management
- Authoritative game state
- Game loop
- Movement calculation
- Collision and combat logic in later milestones
- State synchronization

#### Shared Package

A dedicated Python package containing:

- Network protocol definitions
- Message schemas
- Shared data types
- Protocol version
- Coordinate conventions
- Constants

Use Pydantic for network message validation where appropriate.

The Shared package must not depend on Ursina, Panda3D, FastAPI, or application-specific implementations.

#### Database

No database is required for the initial prototype.

Use in-memory state management.

#### Package Management

Use **uv Workspace**.

The repository must contain a single root workspace with a single shared lockfile.

Each application must have its own `pyproject.toml`, but workspace dependencies should be resolved through the root `uv.lock`.

---

### 4. Monorepo Architecture

Use the following target project structure:

```text
shooting-fighter/
│
├── game-client/
│   ├── src/
│   │   └── shooting_fighter_client/
│   │       ├── __init__.py
│   │       ├── __main__.py
│   │       ├── main.py
│   │       ├── core/
│   │       │   └── game.py
│   │       ├── entities/
│   │       │   ├── local_player.py
│   │       │   └── remote_player.py
│   │       ├── scenes/
│   │       │   └── arena.py
│   │       ├── input/
│   │       │   └── input_handler.py
│   │       ├── networking/
│   │       │   └── network_client.py
│   │       └── config/
│   │           └── settings.py
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
│
├── game-server/
│   ├── src/
│   │   └── shooting_fighter_server/
│   │       ├── __init__.py
│   │       ├── main.py
│   │       ├── core/
│   │       │   ├── config.py
│   │       │   └── game_loop.py
│   │       ├── entities/
│   │       │   └── player.py
│   │       ├── rooms/
│   │       │   ├── room.py
│   │       │   └── room_manager.py
│   │       ├── systems/
│   │       │   └── movement_system.py
│   │       └── networking/
│   │           └── connection_manager.py
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
│
├── shared/
│   ├── src/
│   │   └── shooting_fighter_shared/
│   │       ├── __init__.py
│   │       ├── constants.py
│   │       ├── protocols.py
│   │       ├── messages.py
│   │       └── models/
│   │           ├── player_state.py
│   │           └── game_state.py
│   ├── tests/
│   └── pyproject.toml
│
├── docs/
│   ├── architecture.md
│   ├── network-protocol.md
│   └── development-roadmap.md
│
├── .github/
│   └── workflows/
│
├── .python-version
├── .gitignore
├── pyproject.toml
├── uv.lock
├── AGENTS.md
└── README.md
```

This is the target architecture.

Do not generate every file immediately. Create only files necessary for the current milestone.

---

### 5. uv Workspace Configuration

Configure a single uv workspace at the repository root.

Root `pyproject.toml` should use:

```toml
[tool.uv.workspace]
members = [
    "game-client",
    "game-server",
    "shared",
]
```

Use proper Python package names:

- `shooting-fighter-client`
- `shooting-fighter-server`
- `shooting-fighter-shared`

Both applications must depend on the shared package using uv workspace dependencies.

Example dependency declaration:

```toml
[project]
dependencies = [
    "shooting-fighter-shared",
]

[tool.uv.sources]
shooting-fighter-shared = { workspace = true }
```

Include application-specific dependencies alongside the shared dependency.

Use standard Python packaging with `src/` layout.

Do not use relative filesystem imports between workspace members.

Example shared import:

```python
from shooting_fighter_shared.messages import PlayerInput
```

Do not duplicate network message models inside the client or server.

---

### 6. Architecture Principles

Use **Server-Authoritative Client–Server Architecture**.

#### Client Responsibilities

The client is responsible for:
- Rendering the game world
- Capturing keyboard and mouse input
- Sending player input to the server
- Displaying authoritative game state
- Interpolating remote player positions
- Showing user interface elements

The client must not be trusted to determine:
- Actual player position
- Damage
- Health
- Hit detection
- Scores

#### Server Responsibilities

The server is responsible for:
- Managing connected players
- Managing game rooms
- Validating client messages
- Processing player input
- Calculating authoritative movement
- Updating game state
- Broadcasting snapshots
- Removing disconnected players

Keep the game simulation independent of FastAPI transport implementations.

#### Shared Responsibilities

The shared package defines the communication contract between the client and server.

It must contain no application runtime state.

---

### 7. Networking Architecture

Use WebSocket over TCP with JSON messages for the prototype.

Default development endpoint:

`ws://127.0.0.1:8000/ws`

Use configurable networking settings.

#### Communication Flow

1. Client connects to Server.
2. Server assigns a unique player ID.
3. Server adds the player to the default battle room.
4. Server sends a welcome message.
5. Client sends movement input.
6. Server validates the input.
7. Server processes movement during the game tick.
8. Server broadcasts authoritative snapshots.
9. Clients update their rendered player objects.
10. Server removes disconnected players.

#### Protocol Version

Start with Protocol Version 1.

All message types must be defined in the shared package.

Required messages:
- `welcome`
- `input`
- `snapshot`
- `player_joined`
- `player_left`
- `error`

Example Client → Server:

```json
{
  "type": "input",
  "sequence": 1,
  "payload": {
    "forward": true,
    "backward": false,
    "left": false,
    "right": false,
    "yaw": 90.0
  }
}
```

Example Server → Client:

```json
{
  "type": "snapshot",
  "tick": 120,
  "players": [
    {
      "id": "player_1",
      "x": 1.0,
      "y": 1.0,
      "z": 2.0,
      "yaw": 90.0
    },
    {
      "id": "player_2",
      "x": 4.0,
      "y": 1.0,
      "z": 2.0,
      "yaw": 180.0
    }
  ]
}
```

Use a consistent coordinate system throughout the project.

For Ursina, use Y as the vertical axis.

Explicitly document yaw conventions, world boundaries, movement speed, and player origin.

Validate message types, payload sizes, sequence numbers, and allowed input values.

---

### 8. Game Loop Architecture

Implement a fixed-step simulation loop using Python asyncio.

Initial configuration:

- Server Tick Rate: 20 Hz
- Tick Interval: 50 ms
- Maximum Players per Room: 4
- Initial Room Count: 1
- Snapshot Rate: configurable

The server game loop should:

1. Read the latest validated player inputs.
2. Calculate movement.
3. Apply movement constraints.
4. Update authoritative player state.
5. Generate snapshots.
6. Broadcast snapshots at the configured rate.

Use a monotonic clock and bounded catch-up behavior.

Avoid blocking operations inside the game loop.

Do not perform database queries or expensive I/O inside tick processing.

The initial 20 Hz rate is a prototype starting point, not a production FPS performance guarantee.

---

### 9. Game Client Architecture

Use Ursina for game rendering.

#### Scene

Create a low-poly arena containing:
- Flat ground
- Four boundary walls
- Basic lighting
- Simple sky
- Player spawn points

Do not require external 3D assets.

Use built-in cubes and simple geometric objects.

#### Player Controls

Initial controls:
- W: Move forward
- S: Move backward
- A: Strafe left
- D: Strafe right
- Mouse: Camera direction

Prioritize synchronized movement during Milestone 1.

Advanced physics, jumping, shooting, and client-side prediction are later milestones.

#### Networking

The network client must:
- Connect asynchronously
- Send player input
- Receive server messages
- Handle disconnects
- Support configurable server address
- Transfer received states to the rendering system

Critical rule:

**Never block the Ursina rendering loop with network operations.**

If using a background networking thread, transfer events to the main thread using a thread-safe queue.

Do not modify Ursina entities from background threads.

Keep visual effects independent of network state calculation.

---

### 10. Room Management

The server initially supports one battle room.

Room configuration:
- Room Name: `battle`
- Maximum Players: 4
- Matchmaking: automatic join
- Authentication: not required
- Persistence: in-memory

Each room manages:
- Connected players
- Player state
- Player input
- Game tick lifecycle

The Room Manager must support:
- Create room
- Get room
- Join room
- Leave room
- Player cleanup

Do not build a distributed room system or sophisticated matchmaking during Milestone 1.

---

### 11. Development Milestones

#### Milestone 1 — Multiplayer Foundation

Goal:

Two Ursina clients connect to one FastAPI server and see each other's movement in the same arena.

Server:
- FastAPI application
- WebSocket endpoint
- Connection manager
- Room manager
- Player state
- Game loop
- Movement system
- Snapshot broadcasting

Client:
- Ursina application
- Basic 3D arena
- Player entities
- Keyboard input
- Network client
- Remote player rendering
- Movement synchronization

Shared:
- Protocol version
- Message models
- Player state models
- Constants

Acceptance Criteria:
- Server starts successfully.
- Two clients can connect concurrently.
- Both clients enter the same room.
- Players see each other.
- WASD movement updates remote player positions.
- Disconnecting a client removes that player.
- Server stays running after disconnects.
- Automated tests pass.

Do not proceed to Milestone 2 before review.

#### Milestone 2 — FPS Controller

- First-person camera refinements
- Mouse look improvements
- Jumping
- Gravity
- World collision
- Remote player interpolation
- Smooth movement

#### Milestone 3 — Combat System

- Weapon prototype
- Shooting input
- Server-side hit detection
- Damage calculations
- Health system
- Respawn
- Basic scoreboard

#### Milestone 4 — Network Optimization

- Client-side prediction
- Server reconciliation
- Lag compensation
- Network latency monitoring
- Snapshot optimization

#### Milestone 5 — Production Preparation

Only after the prototype is functional:

- Authentication
- Multiple rooms
- Database integration
- Player profiles
- Match history
- Deployment
- Monitoring
- Load testing

Django may be introduced later as a dedicated account and business API if justified.

---

### 12. Coding Standards

All Python code must:
- Include type hints.
- Follow PEP 8.
- Use Ruff for linting and formatting.
- Prefer small, focused modules.
- Avoid unnecessary inheritance.
- Follow composition where appropriate.
- Use explicit interfaces at important boundaries.
- Avoid circular imports.
- Use structured logging where practical.
- Avoid unexplained magic values.
- Be testable independently of the rendering engine.

Keep the authoritative game simulation separate from networking infrastructure.

Use dependency injection where it simplifies testing, but avoid introducing a DI framework unnecessarily.

Do not apply design patterns only for the sake of using patterns.

---

### 13. Testing Strategy

Use pytest.

#### Server Tests

Test:
- Player joins room
- Player leaves room
- Room capacity
- Movement calculation
- Boundary validation
- Invalid input rejection
- Disconnect cleanup

#### Shared Tests

Test:
- Message serialization
- Message validation
- Protocol compatibility
- Invalid message payloads

#### Client Tests

Test non-rendering logic:
- Input serialization
- Snapshot parsing
- Player state mapping
- Interpolation calculations

#### Integration Tests

Validate:
- Server accepts connections.
- Two clients can join.
- Inputs update server state.
- State snapshots reach connected clients.
- Disconnecting one client does not terminate the server.

Do not require an actual graphics display for headless unit tests.

Document manual rendering and multiplayer testing steps separately.

---

### 14. Human-in-the-loop (HITL)

Work incrementally using clear checkpoints.

#### Before Implementation

- Inspect the existing repository.
- Review current architecture.
- Explain the proposed implementation.
- Identify affected files.
- Identify technical trade-offs.

#### During Implementation

- Implement one focused increment at a time.
- Run tests after meaningful changes.
- Report actual failures.
- Do not silently introduce major architecture changes.
- Do not install unrelated dependencies.
- Do not implement features outside the active milestone.

#### Approval Required

Request human approval before:
- Introducing a new major framework
- Changing the networking protocol incompatibly
- Adding a database
- Adding external services
- Changing the project architecture
- Moving to the next milestone
- Introducing major dependencies unrelated to the active milestone

For routine implementation decisions within an approved milestone, proceed without unnecessary interruptions.

#### After Each Milestone

Provide:
1. Implementation summary
2. Files created or modified
3. Test results
4. Commands to run applications
5. Manual testing instructions
6. Known limitations
7. Proposed next milestone

Stop at the milestone boundary for human review.

---

### 15. AGENTS.md Requirements

Create a root `AGENTS.md` containing:
- Project overview
- Monorepo rules
- Architectural boundaries
- Dependency rules
- Testing requirements
- HITL guidelines
- Current milestone

The root AGENTS.md applies to the entire repository.

Nested AGENTS.md files may be added later when client-specific or server-specific instructions become necessary.

Do not duplicate the entire root context into every subdirectory.

---

### 16. Initial Development Assignment

Start with Milestone 1.

Your first assignment is to establish the development foundation of Shooting Fighter.

Implementation sequence:

1. Inspect the current repository.
2. Set up the uv workspace.
3. Create the Game Server package.
4. Create the Game Client package.
5. Create the Shared package.
6. Define Protocol v1.
7. Implement WebSocket connection handling.
8. Implement basic room management.
9. Create the Ursina arena.
10. Connect Client and Server.
11. Synchronize player movement.
12. Verify with two independent client processes.

Do not implement combat, database, login, inventory, or deployment yet.

### Definition of Done

Two independent instances of `shooting-fighter-client` must successfully connect to one `shooting-fighter-server`, join the same room, and display synchronized player movement within a shared 3D arena.

The implementation must use Python, uv Workspace, a shared protocol package, and a server-authoritative architecture.

**Begin by inspecting the repository and presenting the implementation plan. After the plan, proceed with the minimal Milestone 1 foundation unless a major architectural decision requires approval.**
