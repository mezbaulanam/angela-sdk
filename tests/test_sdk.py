from __future__ import annotations

import json
from angela_sdk import (
    ActionRow,
    Button,
    Container,
    Context,
    Embed,
    Game,
    Section,
    Select,
    SelectOption,
    Separator,
    TextDisplay,
    TextInput,
    Thumbnail,
    dispatch,
)


SAMPLE_EVENT = {
    "event_type": "COMMAND",
    "event_id": "start",
    "guild_id": 905194979650052208,
    "channel_id": 1321720365189300234,
    "user": {
        "id": 496644923601453076,
        "name": "Ray_quaza",
        "avatar_url": "https://cdn.discordapp.com/avatars/496644923601453076/abc.png",
    },
    "args": {
        "subcommand": None,
        "raw_args": "all",
        "target_user_id": 112233445566778899,
        "modal_inputs": {"secret_number": "42"},
        "select_values": ["moon_talisman", "aqua_lens"],
        "message_content": "42",
        "callback_data": {},
    },
    "session": {
        "session_id": "sess_a1b2c3d4",
        "round": 2,
        "participants": [496644923601453076, 112233445566778899],
        "status": "ACTIVE",
        "state": {
            "rod_col": 2,
            "rod_row": 1,
            "fish_spots": [{"col": 1, "row": 0, "fish_id": "sapphire_sardine"}],
        },
    },
    "config": {
        "ui_theme": "CV2",
        "currency_name": "Shells",
        "cooldown_seconds": 20,
    },
    "secrets": {
        "admin_key": "private_val",
    },
}


def test_context_parsing():
    ctx = Context(SAMPLE_EVENT)
    assert ctx.event_type == "COMMAND"
    assert ctx.event_id == "start"
    assert ctx.guild_id == 905194979650052208
    assert ctx.channel_id == 1321720365189300234
    assert ctx.user.id == 496644923601453076
    assert ctx.user.name == "Ray_quaza"
    assert ctx.host_id == 496644923601453076
    assert ctx.args.target_user_id == 112233445566778899
    assert ctx.args.modal_inputs["secret_number"] == "42"
    assert ctx.session.session_id == "sess_a1b2c3d4"
    assert ctx.round == 2
    assert ctx.state["rod_col"] == 2
    assert ctx.config["ui_theme"] == "CV2"
    assert ctx.secrets["admin_key"] == "private_val"


def test_economy_intents():
    ctx = Context(SAMPLE_EVENT)
    ctx.economy.get_balance(ctx.user.id)
    ctx.economy.give(ctx.user.id, 50, reason="Won prize", clamp_min=0, clamp_max=500, currency="Gold")
    ctx.economy.take(ctx.user.id, 20, reason="Fee")
    ctx.economy.escrow_lock(ctx.user.id, 100, reason="Bet", currency="Diamonds")
    ctx.economy.escrow_release(ctx.user.id, 100, reason="Paid out")
    ctx.economy.escrow_refund(ctx.user.id, 100, reason="Refunded")
    ctx.economy.auto_buy(ctx.user.id, ["rod", "bait"], quantity=5)

    res = ctx.to_response()
    assert len(res["intents"]) == 7
    assert res["intents"][0]["op"] == "ECONOMY_MUTATE"
    assert res["intents"][0]["action"] == "GET_BALANCE"
    assert "currency" not in res["intents"][0]
    assert res["intents"][1]["action"] == "GIVE"
    assert res["intents"][1]["amount"] == 50
    assert res["intents"][1]["clamp_max"] == 500
    assert res["intents"][1]["currency"] == "Gold"
    assert res["intents"][2]["action"] == "TAKE"
    assert "currency" not in res["intents"][2]
    assert res["intents"][3]["action"] == "ESCROW_LOCK"
    assert res["intents"][3]["currency"] == "Diamonds"
    assert res["intents"][6]["action"] == "AUTO_BUY"


def test_inventory_intents():
    ctx = Context(SAMPLE_EVENT)
    ctx.inventory.get_server_items(ctx.user.id)
    ctx.inventory.consume_server_item(ctx.user.id, "potion", qty=1)
    ctx.inventory.give_server_item(ctx.user.id, "potion", qty=2)
    ctx.inventory.roll_break(ctx.user.id, "fishing_rod", probability=0.075)
    ctx.inventory.add_sub_item(ctx.user.id, "sapphire_sardine", qty=1)
    ctx.inventory.remove_sub_item(ctx.user.id, "sapphire_sardine", qty=1)

    res = ctx.to_response()
    assert len(res["intents"]) == 6
    assert res["intents"][0]["op"] == "INVENTORY_MUTATE"
    assert res["intents"][3]["action"] == "ROLL_BREAK"
    assert res["intents"][3]["break_chance"] == 0.075


def test_ui_intents():
    ctx = Context(SAMPLE_EVENT)
    btn = Button(custom_id="test_btn", label="Click Me", style="primary", emoji="🚀")
    sel = Select(
        custom_id="test_sel",
        options=[SelectOption(label="Choice A", value="a", description="First")],
    )

    ctx.ui.render(
        title="Title",
        subtitle="Subtitle",
        body_lines=["Line 1", "Line 2"],
        buttons=[btn],
        selects=[sel],
        accent_color="#5865F2",
    )

    ctx.ui.reply_ephemeral(text="Secret info")
    ctx.ui.open_modal(
        title="Input Modal",
        inputs=[TextInput(custom_id="txt", label="Your Answer")],
        callback_id="on_modal_submit",
    )

    res = ctx.to_response()
    assert len(res["intents"]) == 3
    assert res["intents"][0]["op"] == "UI_RENDER"
    assert res["intents"][0]["layout"]["title"] == "Title"
    assert res["intents"][0]["layout"]["accent_color"] == 0x5865F2
    assert res["intents"][1]["ephemeral"] is True
    assert res["intents"][2]["op"] == "UI_MODAL"


def test_canvas_fluent_builder():
    ctx = Context(SAMPLE_EVENT)
    scene = ctx.canvas.create(width=640, height=360)
    bg = scene.layer("background", cache_key="base_v1")
    bg.linear_gradient([0, 0, 640, 300], [25, 45, 95], [240, 140, 90], gamma=1.2)
    bg.celestial_body(320, 140, 20, 70, [255, 245, 210], [255, 190, 80, 90])
    bg.sine_waves(170, 260, 12, [255, 255, 255, 60])

    fg = scene.layer("foreground")
    fg.sprite("fish_blue.png", 300, 185, max_w=62, max_h=62)
    fg.avatar(ctx.user.id, 200, 65, size=80, circular=True)
    fg.progress_bar([50, 20, 250, 36], value=75, max_value=100, bg_color=[20, 20, 30], fill_color=[87, 242, 135])
    fg.text_box([30, 250, 610, 415], "Hello Canvas", size=14)

    ctx.ui.render(title="Canvas Test", image=scene)
    res = ctx.to_response()
    assert "canvas_scene" in res["intents"][0]
    canvas_data = res["intents"][0]["canvas_scene"]
    assert canvas_data["width"] == 640
    assert len(canvas_data["layers"]) == 2
    assert canvas_data["layers"][0]["id"] == "background"
    assert canvas_data["layers"][0]["cache_key"] == "base_v1"


def test_other_subcontexts():
    ctx = Context(SAMPLE_EVENT)
    ctx.lobby.create_join_lobby(max_players=20, duration=60, on_start="start_event")
    ctx.lobby.create_duo_invite(1122334455, entry_fee=15, on_accept="invite_accepted")
    ctx.lobby.exclusive_claim_grid(5, [1, 2, 3], timeout=15)
    ctx.ai.generate_json("System prompt", "User prompt", tier="ai_high", callback="on_ai")
    ctx.media.search_gif("dancing cat", callback="on_gif")
    ctx.http.get("https://api.example.com/data", callback="on_http")
    ctx.discord.lock_channel(duration_seconds=30)
    ctx.discord.listen_messages(exact_match="42", callback="on_msg")
    ctx.storage.set("my_key", 12345)
    assert ctx.storage.get("my_key") == 12345
    ctx.storage.set_cooldown(ctx.user.id, 60)
    ctx.sleep(10, callback="wake_cb")

    res = ctx.to_response()
    assert res["status"] == "SLEEPING"
    assert res["updated_state"]["my_key"] == 12345
    ops = [it["op"] for it in res["intents"]]
    assert "LOBBY_OP" in ops
    assert "AI_GENERATE" in ops
    assert "MEDIA_SEARCH_GIF" in ops
    assert "HTTP_REQUEST" in ops
    assert "CHANNEL_LOCK" in ops
    assert "LISTEN_MESSAGES" in ops
    assert "STORAGE_MUTATE" in ops
    assert "SCHEDULE_WAKE" in ops


def test_game_routing():
    game = Game()

    @game.on_command()
    def on_start(ctx: Context):
        ctx.state["started"] = True
        ctx.ui.render(title="Started!")

    @game.on_button("click_me")
    def on_click(ctx: Context):
        ctx.state["clicked"] = True

    # Test command routing
    cmd_res = game.handle(SAMPLE_EVENT)
    assert cmd_res["status"] == "ACTIVE"
    assert cmd_res["updated_state"]["started"] is True
    assert len(cmd_res["intents"]) == 1

    # Test button routing
    btn_event = dict(SAMPLE_EVENT)
    btn_event["event_type"] = "BUTTON"
    btn_event["event_id"] = "click_me"
    btn_res = game.handle(btn_event)
    assert btn_res["updated_state"]["clicked"] is True


def test_dispatch_helper():
    def custom_handler(ctx: Context):
        ctx.ui.reply_ephemeral(text="Handled via dispatch")

    res = dispatch(custom_handler, SAMPLE_EVENT)
    assert res["status"] == "ACTIVE"
    assert len(res["intents"]) == 1
    assert res["intents"][0]["ephemeral"] is True

