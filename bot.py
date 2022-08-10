import lightbulb
import string

from util import required_env_var, command, option, str_to_bytes
from dotenv import load_dotenv
from functools import wraps
from base64 import b64encode, b64decode

load_dotenv()
bot_token = required_env_var("FLAG_BOT_TOKEN")
bot = lightbulb.BotApp(token=bot_token)

@command(bot, "b64encode", "Encodes text as base64")
@option("input", "Text to encode", required=True)
async def b64encode_cmd(ctx: lightbulb.Context):
    encoded = b64encode(str_to_bytes(ctx.options.input)).decode("utf8")
    await ctx.respond(f"`{encoded}`")

@command(bot, "b64decode", "Decodes text from base64")
@option("input", "Text to decode", required=True)
async def b64decode_cmd(ctx: lightbulb.Context):
    try:
        decoded = str(b64decode(ctx.options.input))[2:-1]
        await ctx.respond(f"`{decoded}`")
    except:
        await ctx.respond("Invalid input")

def caesar_shift(text: str, shift: int) -> str:
    output = ""
    for c in text:
        if not c.isalpha():
            output += c
        else:
            alphabet = string.ascii_lowercase if c.islower() else string.ascii_uppercase
            index = (alphabet.index(c) + shift) % 26
            output += alphabet[index]
    return output

@command(bot, "caesar", "Performs a caesar shift on input text")
@option("input", "Text to shift", required=True)
@option("shift", "Shift to apply", type=int, required=True)
async def caesar_cmd(ctx: lightbulb.Context):
    output = caesar_shift(ctx.options.input, ctx.options.shift)
    await ctx.respond(f"`{output}`")

@command(bot, "brute-caesar", "Applies every possible caesar shift")
@option("input", "Text to shift", required=True)
async def brute_caesar_cmd(ctx: lightbulb.Context):
    output = "```\n"
    for i in range(1, 26):
        output += f"{str(i).rjust(2, '0')}: {caesar_shift(ctx.options.input, i)}"
        output += "\n"
    output += "```"
    await ctx.respond(output)

bot.run()
