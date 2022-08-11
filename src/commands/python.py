import func_timeout
import lightbulb
import hikari

from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

from ..crypto import b64encode_str, b64decode_to_str, caesar_shift
from ..util import command, option

plugin = lightbulb.Plugin("python")

@plugin.listener(hikari.MessageCreateEvent)
async def eval_python(event: hikari.MessageCreateEvent):
    mentioned_member_ids = [member.id for member in event.message.get_member_mentions().values()]
    if mentioned_member_ids != [plugin.bot.get_me().id]:
        return

    lang = None
    code_lines = []
    in_code_block = False
    lines = event.message.content.split("\n")
    for line in lines:
        if in_code_block:
            if line.startswith("```"):
                break
            code_lines.append(line)
        elif line.startswith("```"):
            lang = line[3:]
            in_code_block = True

    if not in_code_block:
        return

    if not lang in ["py", "python"]:
        await event.message.respond("Only python is supported")
        return

    code = "\n".join(code_lines)

    stream = StringIO()
    with redirect_stdout(stream):
        with redirect_stderr(stream):
            def run():
                return exec(code)

            timeout = 2
            try:
                func_timeout.func_timeout(timeout, run)
            except Exception as e:
                await event.message.respond(f"**Error while running code**:\n```\n{e}\n```")
                return
            except func_timeout.FunctionTimedOut:
                await event.message.respond(f"Execution time exceeded timeout ({timeout} seconds)")
                return

    output = stream.getvalue().strip()
    if len(output) == 0:
        await event.message.respond("No output")
    else:
        await event.message.respond(f"```\n{output}\n```")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
