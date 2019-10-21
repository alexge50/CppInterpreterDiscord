import discord
from discord.ext import commands

import subprocess
import re


def cling(code, args):
    cling_jail = [
        'nsjail',
        '--config', 'interpreter-jail.cfg',
        '--really_quiet',
        '--', '/usr/bin/cling', *args]
    result = subprocess.Popen(cling_jail,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).communicate(code.encode())
    return result[0].decode()[177:].strip(), result[1].decode().strip()


bot = commands.Bot(command_prefix='>')


@bot.event
async def on_ready():
    print('running as {0.user}'.format(bot))


@bot.command()
async def eval(ctx, *, args):
    stdout, stderr = cling(args, ['-std=c++17'])
    print(stdout, stderr)

    if stderr == '':
        await ctx.send(f'```cpp\n{stdout}\n```')
    else:
        await ctx.send(f'```\n{stderr}\n```')


@bot.command()
async def eval_block(ctx, *, args):
    code_pattern = re.compile('```(cpp)?[\s\S]*```')
    cli_arguments = code_pattern.sub('', args).strip()
    code_block = code_pattern.search(args).group()

    code_block = code_block[6:] if code_block[:6] == '```cpp' else code_block[3:]
    code_block = code_block[:-3]

    stdout, stderr = cling(code_block, cli_arguments.split(' '))
    print(stdout, stderr)

    if stderr == '':
        await ctx.send(f'```cpp\n{stdout}\n```')
    else:
        await ctx.send(f'```\n{stderr}\n```')

with open('token', 'r') as f:
    token = f.read()
bot.run(token.strip())
