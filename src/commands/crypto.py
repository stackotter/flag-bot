import lightbulb

from ..crypto import b64encode_str, b64decode_to_str, caesar_shift
from ..util import command, option

plugin = lightbulb.Plugin("crypto")

@command(plugin, "b64encode", "Encodes text as base64")
@option("input", "Text to encode", required=True)
async def b64encode_cmd(ctx: lightbulb.Context):
    encoded = b64encode_str(ctx.options.input)
    await ctx.respond(f"`{encoded}`")

@command(plugin, "b64decode", "Decodes text from base64")
@option("input", "Text to decode", required=True)
async def b64decode_cmd(ctx: lightbulb.Context):
    try:
        decoded = b64decode_to_str(ctx.options.input)
        await ctx.respond(f"`{decoded}`")
    except:
        await ctx.respond("Invalid input")

@command(plugin, "caesar", "Performs a caesar shift on input text")
@option("input", "Text to shift", required=True)
@option("shift", "Shift to apply", type=int, required=True)
async def caesar_cmd(ctx: lightbulb.Context):
    output = caesar_shift(ctx.options.input, ctx.options.shift)
    await ctx.respond(f"`{output}`")

@command(plugin, "brute-caesar", "Applies every possible caesar shift")
@option("input", "Text to shift", required=True)
async def brute_caesar_cmd(ctx: lightbulb.Context):
    output = "```\n"
    for i in range(1, 26):
        output += f"{str(i).rjust(2, '0')}: {caesar_shift(ctx.options.input, i)}"
        output += "\n"
    output += "```"
    await ctx.respond(output)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
