import re

import discord
from discord.ext import commands

import interpreters

bot = commands.Bot(command_prefix='>')


@bot.event
async def on_ready():
    print('running as {0.user}'.format(bot))


@bot.command()
async def eval(ctx, *, args):
    stdout, stderr, return_code = interpreters.cling(args, ['-std=c++17'])

    message = f'Return Code: {return_code}\n'

    if stdout is not None:
        message += f'stdout:\n```cpp\n{stdout}\n```'

    if stderr is not None:
        message += f'stderr:\n```fix\n{stderr}\n```'

    await ctx.send(message)


@bot.command()
async def eval_block(ctx, *, args):
    code_pattern = re.compile(r'```(cpp)?(?P<code>[\s\S]*)```')
    cli_arguments = code_pattern.sub('', args).strip()
    code_block = code_pattern.search(args)['code']

    stdout, stderr, return_code = interpreters.cling(code_block, cli_arguments.split(' '))

    message = f'Return Code: {return_code}\n'

    if stdout is not None:
        message += f'stdout:\n```cpp\n{stdout}\n```'

    if stderr is not None:
        message += f'stderr:\n```fix\n{stderr}\n```'

    await ctx.send(message)


with open('token', 'r') as f:
    token = f.read()
bot.run(token.strip())
