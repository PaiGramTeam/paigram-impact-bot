from asyncio import run
from inspect import iscoroutinefunction

from paigram_bot_contracts import BotPlatform, TextResponse
from paigram_bot_core import RuntimePluginConfig, TemplateRuntimeObjects
from paigram_bot_telegram import TelegramBotRuntime, TelegramRuntimeObjects

from paigram_impact_bot import (
    ImpactBotHarnessConfig,
    build_impact_bot_harness,
    with_builtin_system_plugins,
    with_system_start,
)
from paigram_impact_bot.plugins.system_help import SYSTEM_HELP_HANDLERS, SYSTEM_HELP_PLUGIN
from paigram_impact_bot.plugins.system_start import (
    PING_TEXT,
    PRIVACY_TEXT,
    START_TEXT,
    SYSTEM_START_HANDLERS,
    SYSTEM_START_PLUGIN,
    ping_command,
    privacy_command,
    start_command,
)


class FakeTelegramRuntime:
    def register_handler_declarations(self, declarations):
        return self


class FakeImageRenderer:
    async def render_png(self, template, data, *, viewport=None, selector=None, wait_until="load"):
        return b"png"


class FakeTelegramApplication:
    def __init__(self):
        self.handlers = []

    def add_handler(self, handler):
        self.handlers.append(handler)


class FakeBot:
    def __init__(self):
        self.sent_messages = []

    async def send_message(self, *, chat_id, text, parse_mode=None, disable_web_page_preview=None):
        self.sent_messages.append(
            {
                "chat_id": str(chat_id),
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": disable_web_page_preview,
            }
        )


class FakeTelegramContext:
    def __init__(self):
        self.bot = FakeBot()


class FakeUser:
    id = 12345
    full_name = "Tester"


class FakeChat:
    id = 67890


class FakeMessage:
    text = "/ping"


class FakeUpdate:
    effective_user = FakeUser()
    effective_chat = FakeChat()
    effective_message = FakeMessage()


def build_config():
    return ImpactBotHarnessConfig(
        scanner_packages=("paigram_impact_bot",),
        telegram_runtime_objects=TelegramRuntimeObjects(runtime=FakeTelegramRuntime()),
        template_runtime_objects=TemplateRuntimeObjects(image_renderer=FakeImageRenderer()),
    )


def build_config_without_template_runtime():
    return ImpactBotHarnessConfig(
        scanner_packages=("paigram_impact_bot",),
        telegram_runtime_objects=TelegramRuntimeObjects(runtime=FakeTelegramRuntime()),
    )


def test_system_start_plugin_manifest_shape():
    assert SYSTEM_START_PLUGIN.name == "system.start"
    assert SYSTEM_START_PLUGIN.scanner_packages == ["paigram_impact_bot.plugins"]
    assert SYSTEM_START_PLUGIN.platforms == [BotPlatform.TELEGRAM]
    assert SYSTEM_START_PLUGIN.capabilities == ["bot.start"]


def test_system_start_handler_declaration_shape():
    assert SYSTEM_START_HANDLERS.messages == ()
    assert [declaration.command for declaration in SYSTEM_START_HANDLERS.commands] == ["start", "ping", "privacy"]
    assert [declaration.callback for declaration in SYSTEM_START_HANDLERS.commands] == [
        start_command,
        ping_command,
        privacy_command,
    ]
    assert all(declaration.platforms == (BotPlatform.TELEGRAM,) for declaration in SYSTEM_START_HANDLERS.commands)
    assert all(declaration.plugin_name == "system.start" for declaration in SYSTEM_START_HANDLERS.commands)
    assert all(iscoroutinefunction(declaration.callback) for declaration in SYSTEM_START_HANDLERS.commands)


def test_system_start_command_returns_text_response():
    assert run(start_command(object())) == TextResponse(text=START_TEXT)


def test_system_start_ping_returns_legacy_text_response():
    assert run(ping_command(object())) == TextResponse(text=PING_TEXT)
    assert PING_TEXT == "online! ヾ(✿ﾟ▽ﾟ)ノ"


def test_system_start_privacy_returns_markdown_text_response():
    assert run(privacy_command(object())) == TextResponse(
        text=PRIVACY_TEXT,
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
    )


def test_with_system_start_returns_new_config_without_mutating_input():
    config = build_config()

    configured = with_system_start(config)

    assert configured is not config
    assert config.plugin_config.enabled == []
    assert configured.plugin_config.enabled == ["system.start"]
    assert configured.plugins == (SYSTEM_START_PLUGIN,)
    assert configured.handler_declaration_groups == (SYSTEM_START_HANDLERS,)
    assert config.plugins == ()
    assert config.handler_declaration_groups == ()


def test_with_system_start_is_idempotent_for_plugin_name_and_handler_group_identity():
    telegram_objects = TelegramRuntimeObjects(runtime=FakeTelegramRuntime())
    plugin_config = RuntimePluginConfig(enabled=["system.start"])
    config = ImpactBotHarnessConfig(
        scanner_packages=("paigram_impact_bot",),
        plugin_config=plugin_config,
        plugins=(SYSTEM_START_PLUGIN,),
        handler_declaration_groups=(SYSTEM_START_HANDLERS,),
        telegram_runtime_objects=telegram_objects,
    )

    configured = with_system_start(config)

    assert configured.plugin_config is plugin_config
    assert configured.plugins == (SYSTEM_START_PLUGIN,)
    assert configured.handler_declaration_groups == (SYSTEM_START_HANDLERS,)


def test_with_builtin_system_plugins_includes_only_stable_text_plugins():
    config = with_builtin_system_plugins(build_config_without_template_runtime())

    assert config.plugin_config.enabled == ["system.help", "system.start"]
    assert config.plugins == (SYSTEM_HELP_PLUGIN, SYSTEM_START_PLUGIN)
    assert config.handler_declaration_groups == (SYSTEM_HELP_HANDLERS, SYSTEM_START_HANDLERS)


def test_harness_registers_system_start_commands_and_sends_responses(monkeypatch):
    application = FakeTelegramApplication()
    telegram_runtime = TelegramBotRuntime(application)
    telegram_objects = TelegramRuntimeObjects(application=application, runtime=telegram_runtime)

    class FakeCommandHandler:
        def __init__(self, command, callback):
            self.command = command
            self.callback = callback

    monkeypatch.setattr("paigram_bot_telegram.handlers.CommandHandler", FakeCommandHandler)

    config = with_system_start(
        ImpactBotHarnessConfig(
            scanner_packages=("paigram_impact_bot",),
            telegram_runtime_objects=telegram_objects,
        )
    )

    harness = build_impact_bot_harness(config)

    assert harness.bot_runtime.handler_declarations.commands == SYSTEM_START_HANDLERS.commands
    assert harness.bot_runtime.selected_plugins.names == ["system.start"]
    assert [handler.command for handler in application.handlers] == ["start", "ping", "privacy"]

    telegram_context = FakeTelegramContext()
    run(application.handlers[1].callback(FakeUpdate(), telegram_context))
    run(application.handlers[2].callback(FakeUpdate(), telegram_context))

    assert telegram_context.bot.sent_messages == [
        {
            "chat_id": "67890",
            "text": PING_TEXT,
            "parse_mode": None,
            "disable_web_page_preview": None,
        },
        {
            "chat_id": "67890",
            "text": PRIVACY_TEXT,
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": True,
        },
    ]
