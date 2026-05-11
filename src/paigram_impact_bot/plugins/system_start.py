from paigram_bot_contracts import BotPlatform, CommandHandlerDeclaration, PluginHandlerDeclarations, PluginPackage, TextResponse


START_TEXT = "你好！我是 Impact Bot！"
PING_TEXT = "online! ヾ(✿ﾟ▽ﾟ)ノ"
PRIVACY_TEXT = "请查看[PaiGramTeam Bot 用户个人信息及隐私保护政策](https://telegra.ph/paigramteam-bot-privacy-08-02)"

SYSTEM_START_PLUGIN = PluginPackage(
    name="system.start",
    scanner_packages=["paigram_impact_bot.plugins"],
    platforms=[BotPlatform.TELEGRAM],
    capabilities=["bot.start"],
)


async def start_command(context) -> TextResponse:
    return TextResponse(text=START_TEXT)


async def ping_command(context) -> TextResponse:
    return TextResponse(text=PING_TEXT)


async def privacy_command(context) -> TextResponse:
    return TextResponse(
        text=PRIVACY_TEXT,
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
    )


SYSTEM_START_HANDLERS = PluginHandlerDeclarations(
    commands=(
        CommandHandlerDeclaration(
            command="start",
            callback=start_command,
            platforms=(BotPlatform.TELEGRAM,),
            plugin_name="system.start",
            description="Start the Impact Bot.",
        ),
        CommandHandlerDeclaration(
            command="ping",
            callback=ping_command,
            platforms=(BotPlatform.TELEGRAM,),
            plugin_name="system.start",
            description="Check whether Impact Bot is online.",
        ),
        CommandHandlerDeclaration(
            command="privacy",
            callback=privacy_command,
            platforms=(BotPlatform.TELEGRAM,),
            plugin_name="system.start",
            description="Show the PaiGram privacy policy.",
        ),
    )
)
