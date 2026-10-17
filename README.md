# Angela Python SDK (`angela-sdk`)

The official Python SDK for building cartridges in the **Angela Games Ecosystem**.

Angela games run as deterministic WebAssembly cartridges in Discord servers. The SDK provides an ergonomic, decorator-driven framework for handling commands, button clicks, select menus, modals, timed wakes, and real-time multiplayer lobbies.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Architecture & How It Works](#architecture--how-it-works)
4. [Application Lifecycle & Routing](#application-lifecycle--routing)
5. [The Game Context (`ctx`)](#the-game-context-ctx)
6. [Economy & Multi-Currency System](#economy--multi-currency-system)
7. [Inventory & Items](#inventory--items)
8. [UI Engine](#ui-engine)
   - [Universal Render (`ctx.ui.render`)](#universal-render)
   - [Components V2](#components-v2)
   - [Classic Embeds](#classic-embeds)
   - [Modals & Ephemeral Replies](#modals--ephemeral-replies)
9. [2D Canvas Graphics Engine](#2d-canvas-graphics-engine)
   - [Layers & Static Layer Caching](#layers--static-layer-caching)
   - [Complete Drawing API Reference](#complete-drawing-api-reference)
10. [Multiplayer & Lobbies](#multiplayer--lobbies)
11. [AI & Media Gateways](#ai--media-gateways)
12. [HTTP & Discord Utilities](#http--discord-utilities)
13. [Cartridge Project Layout & CLI](#cartridge-project-layout--cli)

---

## Installation

```bash
pip install angela-sdk
```

During local development with the Angela CLI:

```bash
pip install -e /path/to/Angela-sdk
```

Zero external runtime dependencies. Requires Python 3.10+.

---

## Quick Start

Create a minimal interactive game in `main.py`:

```python
from angela_sdk import Game, Button

game = Game("dice_game")

@game.on_command
def start(ctx):
    # Initialize game state
    ctx.state["rolls"] = ctx.state.get("rolls", 0)

    # Render interactive UI
    ctx.ui.render(
        title="🎲 Angela Dice Challenge",
        subtitle=f"Host: {ctx.user.name}",
        body_lines=[
            "Roll the dice to win server currency!",
            f"You have rolled {ctx.state['rolls']} times so far."
        ],
        buttons=[
            Button(custom_id="roll_btn", label="Roll (5 Coins)", style="primary", emoji="🎲"),
            Button(custom_id="cash_out", label="Cash Out", style="danger", emoji="💰"),
        ]
    )

@game.on_button("roll_btn")
def on_roll(ctx):
    import random
    score = random.randint(1, 6)
    ctx.state["rolls"] = ctx.state.get("rolls", 0) + 1

    # Award currency using the server's configured game currency
    reward = score * 10
    ctx.economy.give(ctx.user.id, reward, reason=f"Rolled a {score}!")

    ctx.ui.render(
        title="🎲 Nice Roll!",
        body_lines=[
            f"You rolled a **{score}**!",
            f"Earned: **+{reward} {ctx.config.get('currency_name', 'Coins')}**"
        ],
        buttons=[
            Button(custom_id="roll_btn", label="Roll Again", style="primary", emoji="🎲"),
            Button(custom_id="cash_out", label="Finish", style="secondary"),
        ]
    )

@game.on_button("cash_out")
def on_cash_out(ctx):
    ctx.finish()
    ctx.ui.render(
        title="🏆 Game Over",
        body_lines=[
            f"Thanks for playing, {ctx.user.name}!",
            f"Total rolls: {ctx.state.get('rolls', 0)}"
        ]
    )

# Entry point called by Angela's runtime
handle = game.handle
```

---

## Architecture & How It Works

Angela games use a **declarative intent-based architecture**:

1. **Incoming Event**: When a user runs a slash command, clicks a button, or submits a modal, Angela formats the action into an event and passes it to your cartridge's `handle(event)` function.
2. **Context Creation**: The SDK wraps the event into a rich `Context` (`ctx`) object containing the user, session state, arguments, and slot configuration.
3. **Intent Accumulation**: Your event handlers mutate `ctx.state` and call sub-APIs (such as `ctx.economy.give()`, `ctx.ui.render()`, or `ctx.canvas.create()`). These calls don't make network requests directly; instead, they record **intents** in an execution plan.
4. **Response Dispatch**: The SDK serializes the final session state and accumulated intents into a single response. Angela's host verifies balances, renders UI, executes economy mutations atomically, and posts the results back to Discord.

This model guarantees that game logic remains fast, deterministic, sandboxed, and testable offline.

---

## Application Lifecycle & Routing

### Event Decorators

Register handlers on your `Game` instance:

```python
from angela_sdk import Game

game = Game("my_cartridge")

# Triggered when the game command is invoked
@game.on_command
def handle_command(ctx): ...

# Triggered on subcommands: /game play
@game.on_command("play")
def handle_play(ctx): ...

# Triggered when a button with matching custom_id is clicked
@game.on_button("hit_btn")
def handle_hit(ctx): ...

# Triggered when a select menu value is chosen
@game.on_select("character_picker")
def handle_character(ctx): ...

# Triggered when a modal form is submitted
@game.on_modal("bet_modal")
def handle_bet_input(ctx): ...

# Triggered when chat message listener is active
@game.on_message
def handle_chat_message(ctx): ...

# Triggered after a scheduled hibernation wake
@game.on_wake("boss_turn")
def handle_boss_turn(ctx): ...

# Triggered on async callbacks (AI generation, HTTP responses, GIF search)
@game.on_callback("on_story_ready")
def handle_story_callback(ctx): ...

# Fallback handler when no specific match is found
@game.default
def handle_fallback(ctx): ...
```

### Session States & Lifecycle Control

Every game session tracks its status:

- `ctx.status`: Current state (`"ACTIVE"`, `"SLEEPING"`, `"PAUSED"`, `"FINISHED"`).
- `ctx.finish()`: Marks the game session as complete. Angela archives the session.
- `ctx.pause()`: Pauses interactive turns until resumed.
- `ctx.next_round()`: Increments `ctx.round` by 1 and returns the new round number.
- `ctx.sleep(seconds, callback="on_sleep_complete")`: Pauses execution. Delays over 3 seconds hibernate the session; Angela schedules a wake event and re-invokes `@game.on_wake(callback)` when the timer fires.

---

## The Game Context (`ctx`)

Passed as the primary argument to every handler:

### Metadata & User Info

- `ctx.user.id`: Discord user ID (`int`) of the interacting player.
- `ctx.user.name`: Discord username (`str`).
- `ctx.user.avatar_url`: User avatar image URL (`str`).
- `ctx.host_id`: User ID of the session creator (`int`).
- `ctx.guild_id`: Server ID (`int`).
- `ctx.channel_id`: Channel ID (`int`).
- `ctx.event_type`: Event kind (`"COMMAND"`, `"BUTTON"`, `"SELECT"`, `"MODAL"`, etc.).
- `ctx.event_id`: ID of the triggering component or button.

### User Arguments (`ctx.args`)

- `ctx.args.subcommand`: Subcommand invoked (if any).
- `ctx.args.raw_args`: Unparsed command text arguments.
- `ctx.args.target_user_id`: Target user ID when command mentions another user.
- `ctx.args.select_values`: Selected option values list (`list[str]`).
- `ctx.args.modal_inputs`: Dictionary mapping modal text input `custom_id`s to values (`dict[str, str]`).
- `ctx.args.message_content`: Content of message when triggered via `@game.on_message`.
- `ctx.args.callback_data`: Data payload returned by async host callbacks.

### Session State (`ctx.state`)

`ctx.state` is a standard Python dictionary automatically persisted between turns across Discord interactions.

```python
# Read or write state naturally
ctx.state["round"] = ctx.state.get("round", 1) + 1
ctx.state["deck"] = ["A♠", "K♦", "10♣"]
ctx.state["players"] = [ctx.user.id]
```

### Slot Configuration (`ctx.config`)

Read-only dictionary containing server-specific settings defined in the server's slot configuration (or defaulted from `manifest.json`):

```python
theme = ctx.config.get("ui_theme", "CV2")
currency_name = ctx.config.get("currency_name", "Coins")
currency_emoji = ctx.config.get("currency_emoji", "🪙")
difficulty = ctx.config.get("difficulty", "medium")
```

### Slot Secrets (`ctx.secrets`)

Read-only dictionary holding private credentials configured by the slot owner (e.g., custom third-party API tokens). Secrets are never exposed to clients or persisted in game state.

### Persistent Player Storage (`ctx.storage`)

Store game-scoped persistent data and per-user cooldowns:

```python
# Check or set player state
high_score = ctx.storage.get("high_score", 0)
ctx.storage.set("high_score", max(high_score, current_score))

# Enforce a 60-second cooldown on the current user
ctx.storage.set_cooldown(ctx.user.id, seconds=60)
```

---

## Economy & Multi-Currency System

Angela provides a native server-backed economy engine. Games emit declarative economy intents; Angela safely executes balance checks and mutations.

### Server Currency Integration

Every Discord server configures its preferred game currency on the game slot (e.g. `"Coins"`, `"Shells"`, `"Credits"`). By default, omitting `currency` automatically targets whichever currency the server administrator has chosen:

```python
# Check balance in the server's default game currency
ctx.economy.get_balance(ctx.user.id)

# Deduct cost from the user
ctx.economy.take(ctx.user.id, amount=20, reason="Entry fee")

# Award earnings with optional safety clamping
ctx.economy.give(
    ctx.user.id,
    amount=100,
    reason="Victory bonus",
    clamp_min=0,
    clamp_max=500
)
```

### Explicit Multi-Currency

For multi-currency or trading games, pass an explicit `currency` parameter:

```python
# Target specific currencies
ctx.economy.get_balance(ctx.user.id, currency="Gems")
ctx.economy.give(ctx.user.id, amount=5, reason="Daily gem drop", currency="Gems")
ctx.economy.take(ctx.user.id, amount=50, reason="Purchased skin", currency="Gold")
```

### Escrow (Betting & Duels)

Lock currency during matches. Angela holds the funds in escrow and refunds them automatically if a player declines or an invite expires:

```python
# Lock entry fees into escrow
ctx.economy.escrow_lock(ctx.user.id, amount=50, reason="Duo bet")

# On win: release escrow to winner
ctx.economy.escrow_release(winner_id, amount=100, reason="Won duo match")

# On forfeit / draw / timeout: refund participants
ctx.economy.escrow_refund(ctx.user.id, amount=50, reason="Match drawn")
```

### Auto-Buy Items

Automatically deduct currency to purchase consumable items if the player is missing them:

```python
ctx.economy.auto_buy(ctx.user.id, item_ids=["fishing_bait", "energy_drink"], quantity=5)
```

---

## Inventory & Items

Games interact with both global server items and game-scoped sub-inventories.

### Server Items

```python
# Check user inventory
ctx.inventory.get_server_items(ctx.user.id)

# Consume a usable item
ctx.inventory.consume_server_item(ctx.user.id, item_id="health_potion", qty=1)

# Award a server item
ctx.inventory.give_server_item(ctx.user.id, item_id="trophy_gold", qty=1)

# Roll item durability / break chance (e.g. 7.5% break chance)
ctx.inventory.roll_break(ctx.user.id, item_id="iron_pickaxe", probability=0.075)
```

### Game-Scoped Sub-Inventory

Store game-specific loot (e.g. caught fish, crafted runes, collected cards) without cluttering the server's global item catalog:

```python
# Add item to player's game-specific collection
ctx.inventory.add_sub_item(ctx.user.id, item_id="sapphire_sardine", qty=1)

# Remove or sell item
ctx.inventory.remove_sub_item(ctx.user.id, item_id="sapphire_sardine", qty=1)
```

---

## UI Engine

Angela features a dual-mode UI engine supporting both **Components V2** (modern Discord containers, media galleries, and sections) and **Classic Embeds**.

### Universal Render

`ctx.ui.render()` automatically compiles your layout into the format configured by the server (`AUTO`, `CV2`, or `CLASSIC_EMBED`):

```python
ctx.ui.render(
    title="⚔️ Boss Raid: Abyssal Hydra",
    subtitle="Turn 3 — Party HP: 84%",
    body_lines=[
        "The Hydra charges a venom breath attack!",
        "Choose your defensive stance:"
    ],
    thumbnail="https://example.com/hydra.png",
    accent_color=0x9B59B6,
    buttons=[
        Button(custom_id="defend_shield", label="Raise Shield", style="primary", emoji="🛡️"),
        Button(custom_id="dodge_roll", label="Dodge", style="secondary", emoji="💨"),
        Button(custom_id="heal_party", label="Cast Heal", style="success", emoji="✨"),
    ]
)
```

### Components V2

Build rich modular layouts with `Container`, `Section`, `TextDisplay`, `Thumbnail`, `MediaGallery`, and `Separator`:

```python
from angela_sdk import (
    Container,
    Section,
    TextDisplay,
    Thumbnail,
    MediaGallery,
    Separator,
    ActionRow,
    Button,
)

container = (
    Container(accent_color="#5865F2")
    .add(
        Section(
            text_displays=[
                TextDisplay("## 🏆 Tournament Leaderboard"),
                TextDisplay("Top gladiators of this arena season:")
            ],
            accessory=Thumbnail("https://example.com/trophy.png")
        )
    )
    .add(Separator(divider=True))
    .add(
        ActionRow([
            Button(custom_id="prev_page", label="Previous", style="secondary"),
            Button(custom_id="next_page", label="Next", style="primary"),
        ])
    )
)

ctx.ui.render_cv2(container)
```

### Classic Embeds

```python
from angela_sdk import Embed, Button

embed = (
    Embed(
        title="🎣 Catch Summary",
        description="Here is what you pulled from the depths:",
        color=0x3498DB
    )
    .add_field(name="Species", value="Sapphire Sardine", inline=True)
    .add_field(name="Weight", value="4.2 kg", inline=True)
    .add_field(name="Value", value="35 Shells", inline=True)
)

ctx.ui.render_embed(
    embed=embed,
    components=[
        Button(custom_id="cast_again", label="Cast Line", style="primary", emoji="🎣")
    ]
)
```

### Modals & Ephemeral Replies

```python
from angela_sdk import TextInput

# Open an interactive modal form
@game.on_button("open_bet")
def prompt_bet(ctx):
    ctx.ui.open_modal(
        title="Place Your Wager",
        callback_id="bet_submitted",
        inputs=[
            TextInput(
                custom_id="bet_amount",
                label="Wager Amount",
                placeholder="e.g. 50",
                required=True,
                max_length=6
            )
        ]
    )

# Receive modal input
@game.on_modal("bet_submitted")
def on_bet(ctx):
    amount = int(ctx.args.modal_inputs.get("bet_amount", "0"))
    ctx.economy.take(ctx.user.id, amount, reason="Wager placed")
    ctx.ui.reply_ephemeral(f"Locked in your wager of **{amount} coins**!")
```

### Public Chat Delivery (`send_chat` vs `EDIT_MAIN`)

By default, games update the original game message in-place (`target="EDIT_MAIN"`). This is ideal for lobbies, turn-based card tables, and game boards to prevent chat spam.

However, many games (such as Trivia, battle announcements, or round-by-round logs) require sending **brand-new public messages** without overwriting the original message or being hidden in ephemeral replies.

Use `ctx.ui.send_chat(...)` or set `target="NEW_MESSAGE"`:

```python
# Helper method: sends a new public message to the channel
ctx.ui.send_chat(
    text="🎉 A new trivia round has begun! Answer within 15 seconds!",
    title="🧠 Round 1: Science & Nature",
    buttons=[
        Button(custom_id="ans_a", label="A) Mars", style="primary"),
        Button(custom_id="ans_b", label="B) Venus", style="secondary"),
    ]
)

# Or explicitly via ctx.ui.render:
ctx.ui.render(
    title="📢 Global Announcement",
    body_lines=["Player Ray_quaza just found a Legendary Chest!"],
    target="NEW_MESSAGE",
    ephemeral=False
)
```

| Method / Target | Visibility | Replaces Previous? | Best Used For |
|---|---|---|---|
| `target="EDIT_MAIN"` (Default) | Public | Yes (Edits main message) | Lobbies, boards, scoreboards, casino wheels |
| `ctx.ui.send_chat(...)` / `target="NEW_MESSAGE"` | Public | No (Sends new message) | Trivia rounds, event announcements, elimination logs |
| `ctx.ui.reply_ephemeral(...)` | Only Clicker | No (Private reply) | Secret hands, balance checks, validation errors |

---

## 2D Canvas Graphics Engine

Angela includes a declarative 2D graphics engine. You describe layers and primitives; Angela compiles them into rendered PNGs (or animated GIFs/WebPs) attached directly to your game message.

### Creating a Scene

```python
scene = ctx.canvas.create(
    width=640,
    height=360,
    animated=False,
    filename="game_screen.png"
)
```

### Layers & Static Layer Caching

Layers run in order from bottom to top. Setting a `cache_key` on static background layers caches the rendered graphic on disk — re-renders skip all background pixel operations and composite directly on top:

```python
# Background layer (cached — zero re-render overhead on reuse)
bg = scene.layer("background", cache_key="ocean_sunset_v1")
bg.linear_gradient(rect=[0, 0, 640, 360], start_rgb=[15, 25, 60], end_rgb=[230, 120, 60], gamma=1.2)
bg.celestial_body(x=320, y=120, radius=22, glow_radius=75, color=[255, 240, 200], glow_color=[255, 180, 70, 80])
bg.sine_waves(y_start=180, y_end=280, count=8, color=[255, 255, 255, 50])
bg.vignette(depth=40, intensity=1.1)

# Dynamic entities layer (drawn fresh each turn)
entities = scene.layer("dynamic_entities")
entities.radial_glow(x=300, y=180, radius=35, color=[255, 215, 0], max_alpha=50)
entities.sprite(asset_key="fish_gold.png", x=300, y=180, max_w=64, max_h=64)
entities.avatar(user_id=ctx.user.id, x=40, y=40, size=64, circular=True, border_color=[255, 215, 0], border_width=2)
entities.rounded_rect(rect=[20, 300, 620, 345], radius=8, fill=[15, 20, 35, 200], outline=[255, 255, 255, 60])
entities.progress_bar(rect=[35, 312, 250, 332], value=75, max_value=100, bg_color=[30, 30, 45], fill_color=[87, 242, 135], radius=5)
entities.text_box(rect=[300, 310, 600, 340], text="Reeling in catch...", font="bold", size=14, color=[255, 255, 255])

# Pass canvas scene directly to UI render
ctx.ui.render(
    title="Ocean Explorer",
    image=scene,
    buttons=[Button(custom_id="reel_in", label="Reel!", style="success")]
)
```

### Complete Canvas Drawing API Reference

| Operation | Parameters | Description |
|-----------|------------|-------------|
| `linear_gradient` | `rect, start_rgb, end_rgb, gamma=1.0` | Vertical color blend across rectangle |
| `celestial_body` | `x, y, radius, glow_radius, color, glow_color` | Sun, moon, or glowing orb with smooth radial glow |
| `sine_waves` | `y_start, y_end, count, color` | Procedural ocean waves or stylized horizon ripples |
| `procedural_palm` | `x, y_bottom, y_top, seed=0` | Procedural beach palm tree silhouette |
| `vignette` | `depth, intensity` | Smooth dark edges around canvas border |
| `radial_glow` | `x, y, radius, color, max_alpha=255` | Soft radial light halo |
| `sprite` | `asset_key, x, y, max_w, max_h, anchor, flip_x, rotation` | Draws a PNG image from your cartridge `./assets/` |
| `avatar` | `user_id, x, y, size=80, circular=True, border_color, border_width` | Draws any player's Discord avatar with optional border |
| `polygon` | `points, fill, outline` | Multi-point closed polygon |
| `line` | `points, color, width=1` | Multi-segment line stroke |
| `arc` | `bbox, start_deg, end_deg, color, width=1` | Elliptical or circular arc |
| `rounded_rect` | `rect, radius, fill, outline, width=1` | Smooth rounded box with optional stroke |
| `progress_bar` | `rect, value, max_value, bg_color, fill_color, radius` | Filled progress gauge for HP, XP, or time |
| `text_box` | `rect, text, font, size, color, max_lines, line_height` | Text box with multi-line word wrapping |

---

## Multiplayer & Lobbies

Build multi-user games without having to manually track join lists, timeouts, or race conditions.

### Turnkey Join Lobby

```python
# Create a public lobby that collects participants for 60 seconds
@game.on_command
def start_lobby(ctx):
    ctx.lobby.create_join_lobby(
        max_players=16,
        duration=60,
        on_start="on_lobby_countdown_ended"
    )

@game.on_wake("on_lobby_countdown_ended")
def start_match(ctx):
    players = ctx.session.participants
    ctx.ui.render(
        title="⚔️ Match Begun!",
        body_lines=[f"Total gladiators: {len(players)}"]
    )
```

### Duo Invites with Escrow

```python
# Challenge another player
@game.on_command("challenge")
def challenge_user(ctx):
    target_id = ctx.args.target_user_id
    ctx.lobby.create_duo_invite(
        partner_id=target_id,
        entry_fee=25,
        on_accept="on_duel_accepted"
    )

@game.on_callback("on_duel_accepted")
def on_duel(ctx):
    ctx.ui.render(title="⚔️ Duel Started!", body_lines=["Both players locked in 25 coins!"])
```

### Exclusive Atomic Claim Grid

Prevent button-clicking race conditions in high-speed multiplayer games (e.g. musical chairs, treasure chest rushes):

```python
ctx.lobby.exclusive_claim_grid(
    count=3,
    eligible_users=ctx.session.participants,
    timeout=15,
    on_resolve="on_chests_opened"
)
```

---

## AI & Media Gateways

Trigger host-mediated LLM generations and media searches without bundling heavy external clients:

### Dynamic AI Generation

```python
@game.on_button("ask_oracle")
def call_oracle(ctx):
    ctx.ai.generate_json(
        system_prompt="You are an eccentric dungeon master. Return a JSON object with 'encounter' and 'choices'.",
        user_prompt="The players open a mossy stone door in an underwater temple.",
        tier="ai_low",
        temperature=0.9,
        callback="on_oracle_response"
    )

@game.on_callback("on_oracle_response")
def on_oracle_data(ctx):
    data = ctx.args.callback_data
    ctx.ui.render(
        title="🔮 The Oracle Speaks",
        body_lines=[data.get("encounter", "The waters ripple quietly...")]
    )
```

### GIF Search

```python
ctx.media.search_gif("victory celebration", callback="on_gif_found")
```

---

## HTTP & Safe Network Access

### Safe Outbound HTTP (`ctx.http.get` / `ctx.http.post`)

Angela games execute within a sandboxed WebAssembly (WASM) runtime. Because WASM runtimes have **no raw OS sockets**, standard synchronous networking libraries (such as `requests`, `urllib`, `aiohttp`, or `httpx`) are **strictly prohibited** and will crash at compile or runtime.

Instead, Angela provides a secure **two-phase asynchronous HTTP gateway** via `ctx.http`:
1. **Phase 1 (Request)**: Your cartridge registers an intent with `ctx.http.get(url, callback=...)` or `ctx.http.post(url, json=..., callback=...)`.
2. **Phase 2 (Callback)**: Angela's host verifies the URL against SSRF protection policies, fetches the response safely, and invokes your registered callback handler with the parsed payload in `ctx.args.callback_data`.

```python
@game.on_command("trivia")
def fetch_trivia(ctx):
    # Phase 1: Request data via host proxy
    ctx.http.get(
        url="https://the-trivia-api.com/v2/questions?limit=1",
        callback="on_trivia_received"
    )

@game.on_callback("on_trivia_received")
def on_trivia(ctx):
    # Phase 2: Host hands parsed JSON response in ctx.args.callback_data
    questions = ctx.args.callback_data
    if questions and len(questions) > 0:
        q = questions[0]
        ctx.ui.send_chat(
            title="🧠 Question Time!",
            text=q["question"]["text"],
            buttons=[
                Button(custom_id="ans_correct", label=q["correctAnswer"], style="primary"),
                Button(custom_id="ans_wrong", label=q["incorrectAnswers"][0], style="secondary"),
            ]
        )
```

---

## Sandboxing & Dependency Constraints

To guarantee millisecond-level execution, deterministic security, and cross-platform compatibility across all Discord servers:

1. **Pure Standard Library Only**: Cartridges must rely strictly on standard built-in modules (e.g. `random`, `math`, `datetime`, `json`, `collections`, `itertools`, `re`, `enum`).
2. **No C-Extension Wheels**: External pip packages that require native C/C++ compilation (such as `numpy`, `pandas`, `cryptography`, `pillow`, `pydantic_core`) cannot run in the WASM Component Model.
3. **Official Angela SDK**: Only import the official `angela_sdk` (or `angela-sdk` for TypeScript/JavaScript). All Discord interactions, graphics rendering, economy mutations, and HTTP calls are handled through `ctx`.
4. **Deterministic Storage**: Cartridges cannot write to the host filesystem. Persistent state across rounds must be saved into `ctx.state` or `ctx.storage`.

---

## Discord Utilities

### Channel Management & Chat Listening

```python
# Temporarily lock channel during critical minigame phase
ctx.discord.lock_channel(duration_seconds=30)

# Listen for specific chat answers
ctx.discord.listen_messages(
    exact_match="42",
    callback="on_correct_answer",
    enabled=True
)
```

---

## Cartridge Project Layout & CLI

Use `angela-cli` to scaffold, test, and publish your cartridge.

### Standard File Layout

```text
my_game/
├── manifest.json       # Game metadata, config schema, slot settings
├── main.py             # Entry script exposing handle = game.handle
└── assets/             # Game sprites referenced by ctx.canvas.sprite()
    ├── boss.png
    └── coin.png
```

### `manifest.json` Specification

Angela cartridges require a valid `manifest.json` at project root matching the CLI and API specifications:

```json
{
  "package_id": "dice-master-py",
  "name": "Dice Master Python",
  "version": "0.1.0",
  "language": "python",
  "entrypoint": "main.py",
  "license": "proprietary",
  "public": false,
  "target_guild_id": "905194979650052208",
  "target_slot_id": 1,
  "default_command": "dice-master-py",
  "default_ui_theme": "AUTO",
  "max_flux_per_tick": 5,
  "config_schema": {
    "currency_name": "Coins",
    "currency_emoji": "🪙",
    "cooldown_seconds": 30
  }
}
```

#### Manifest Fields Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `package_id` | `string` | **Yes** | 2–63 lowercase alphanumeric characters (`a-z0-9._-`). Unique cartridge identifier. |
| `name` | `string` | **Yes** | Human-readable cartridge display name. |
| `version` | `string` | **Yes** | Semantic version string (e.g. `"0.1.0"`). |
| `language` | `string` | **Yes** | Cartridge language: `"python"`, `"typescript"`, `"javascript"`, or `"lua"`. |
| `entrypoint` | `string` | **Yes** | Relative path to entry file matching language extension (`.py`, `.ts`, `.js`, `.lua`). |
| `license` | `string` | **Yes** | `"open"` (open source; authorized users can inspect) or `"proprietary"` (author-only code visibility). |
| `public` | `boolean` | **Yes** | Whether to list the cartridge publicly on the Angela marketplace. |
| `target_guild_id` | `string` | **Yes** | Target Discord server guild ID where this cartridge slot lives. |
| `target_slot_id` | `integer` | **Yes** | Target slot ID number on the server (e.g. `1`, `2`). |
| `default_command` | `string` | No | Slash command trigger for this game (defaults to `package_id`). |
| `default_ui_theme` | `string` | No | Default rendering mode: `"AUTO"`, `"CV2"`, or `"CLASSIC_EMBED"`. |
| `max_flux_per_tick` | `integer` | No | Compute Flux ceiling per interaction tick (1 to 100, defaults to 5). |
| `config_schema` | `object` | No | Default server configuration options merged into `ctx.config`. |

### CLI Commands

```bash
# Initialize a new game cartridge
angela init

# Validate syntax, manifest, and dependencies
angela validate

# Run local interactive simulation with simulated Discord events
angela dev

# Authenticate with Discord
angela login

# Upload and deploy cartridge to your server
angela push
```

---

## License

MIT License. Built for the Angela Games Ecosystem.
