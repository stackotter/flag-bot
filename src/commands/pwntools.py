import lightbulb

from ..util import command, option

plugin = lightbulb.Plugin("pwntools")

@command(plugin, "pwntools-template", "Gives you a basic pwntools script")
@option("executable-path", "Path to the executable relative to where the script will be")
@option("remote-addr", "Address of challenge socket if present", required=False)
@option("libc-path", "Path to libc.so to load into script if present", required=False)
async def pwntools_template_cmd(ctx: lightbulb.Context):
    executable_path = ctx.options["executable-path"]
    remote_addr = ctx.options["remote-addr"]
    libc_path = ctx.options["libc-path"]


    template = "from pwn import *\n\n"

    proc_args = ""
    if libc_path:
        proc_args = f", env={{'LD_PRELOAD':'{libc_path}'}}"

    if remote_addr == None:
        template += f"p = process('{executable_path}'{proc_args})\n"
    else:
        parts = remote_addr.split(":")
        if len(parts) != 2:
            await ctx.respond("Expected `remote-addr` to be of the form `host:port`")
            return
        host = parts[0]
        port = parts[1]

        template +=  "run_locally = True\n"
        template +=  "if run_locally:\n"
        template += f"  p = process('{executable_path}'{proc_args})\n"
        template +=  "else:\n"
        template += f"  p = remote('{host}', '{port}')\n"

    if libc_path:
        template += f"\nlibc = ELF('{libc_path}')\n"

    template += "\npayload = 'a'\np.sendline(payload)\n\n"
    template += "print(p.recvall())"

    await ctx.respond(f"```py\n{template}\n```")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
