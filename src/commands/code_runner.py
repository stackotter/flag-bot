import subprocess
import lightbulb
import resource
import tempfile
import asyncio
import shutil
import hikari
import pwd
import sys

from contextlib import redirect_stdout, redirect_stderr, ExitStack
from io import StringIO

from ..message import extract_code_block
from ..env import sandbox_user

plugin = lightbulb.Plugin("code-runner")

@plugin.listener(hikari.MessageCreateEvent)
async def eval_python(event: hikari.MessageCreateEvent):
    mentioned_member_ids = [member.id for member in event.message.get_member_mentions().values()]
    if mentioned_member_ids != [plugin.bot.get_me().id]:
        return

    # Parse message's code block if present
    code_block = extract_code_block(event.message.content)
    if code_block.lang == None:
        await event.message.respond("No language specified, assuming python", reply=True)
        code_block.lang = "python"
    elif not code_block.lang in ["py", "python", "sh"]:
        await event.message.respond("Only python is supported", reply=True)
        return

    # Figure out how to run the code
    extension = "sh" if code_block.lang == "sh" else "py"
    interpreter = "/bin/sh" if code_block.lang == "sh" else sys.executable

    # Create execution directory containing script
    temp_dir = tempfile.mkdtemp()
    temp_file = f"{temp_dir}/script.{extension}"
    with open(temp_file, "w") as f:
        f.write(code_block.code)

    # Give sandbox user access to execution directory
    entry = pwd.getpwnam(sandbox_user)
    sandbox_uid = entry.pw_uid
    sandbox_gid = entry.pw_gid
    shutil.chown(temp_dir, sandbox_uid, sandbox_gid)
    shutil.chown(temp_file, sandbox_uid, sandbox_gid)

    # Clean up execution environment
    def cleanup():
        try:
            entry = pwd.getpwnam(subprocess.check_output(["whoami"]).decode("utf8").strip())
            # Avoid killing important processes if sandbox user is current user (which would be a
            # dev env)
            if sandbox_uid != entry.pw_uid:
                subprocess.run(["pkill", "-u", str(sandbox_uid)])
        except Exception as e:
            asyncio.run_coroutine_threadsafe(event.message.respond(f"**Failed to kill all processes created by snippet**: `{e}`", reply=True), asyncio.get_event_loop())
            return

        shutil.rmtree(temp_dir)

    # Run the code and clean up execution environment no matter what happens
    output = None
    with ExitStack() as stack:
        stack.callback(cleanup)
        try:
            output = subprocess.check_output(
                [interpreter, temp_file],
                stderr=subprocess.STDOUT,
                cwd=temp_dir,
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

    # Handle code output
    output = output.strip()
    if len(output) == 0:
        await event.message.respond("No output", reply=True)
    else:
        await event.message.respond(f"```\n{output}\n```", reply=True)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
