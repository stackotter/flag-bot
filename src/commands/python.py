import subprocess
import lightbulb
import tempfile
import shutil
import hikari
import pwd
import sys

from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

from ..message import extract_code_block
from ..env import sandbox_user

plugin = lightbulb.Plugin("python")

@plugin.listener(hikari.MessageCreateEvent)
async def eval_python(event: hikari.MessageCreateEvent):
    mentioned_member_ids = [member.id for member in event.message.get_member_mentions().values()]
    if mentioned_member_ids != [plugin.bot.get_me().id]:
        return

    code_block = extract_code_block(event.message.content)

    if code_block.lang == None:
        await event.message.respond("No language specified, assuming python", reply=True)
        code_block.lang = "python"
    elif not code_block.lang in ["py", "python"]:
        await event.message.respond("Only python is supported", reply=True)
        return

    # Create execution directory containing script
    temp_dir = tempfile.mkdtemp()
    temp_file = f"{temp_dir}/script.py"
    with open(temp_file, "w") as f:
        f.write(code_block.code)

    # Allow sandbox user access to execution directory and script
    entry = pwd.getpwnam(sandbox_user)
    sandbox_uid = entry.pw_uid
    sandbox_gid = entry.pw_gid
    shutil.chown(temp_dir, sandbox_uid, sandbox_gid)
    shutil.chown(temp_file, sandbox_uid, sandbox_gid)

    try:
        output = subprocess.check_output(
            [sys.executable, temp_file],
            stderr=subprocess.STDOUT,
            timeout=2,
            user=sandbox_uid,
            group=sandbox_gid
        ).decode("utf8")
    except subprocess.CalledProcessError as e:
        response = f"**Process returned non-zero exit status {e.returncode}**"
        if e.output != None and len(e.output.strip()) != 0:
            response += f"\n```\n{e.output.decode('utf8').strip()}\n```"
        await event.message.respond(response, reply=True)
        return
    except Exception as e:
        await event.message.respond(f"**Error while running code**: `{e}`", reply=True)
        return
    output = output.strip()

    shutil.rmtree(temp_dir)

    if len(output) == 0:
        await event.message.respond("No output", reply=True)
    else:
        await event.message.respond(f"```\n{output}\n```", reply=True)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
