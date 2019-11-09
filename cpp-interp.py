import re
import argparse

import discord
from discord.ext import commands

import interpreters

parser = argparse.ArgumentParser(description='C++ Interpreter Python Bot')
parser.add_argument('config', type=str, help='config file')

args = parser.parse_args()

with open(args.config) as f:
    import json
    config = json.load(f)

bot = commands.Bot(command_prefix=config['prefix'])
interpreters.nsjail_bin = config['nsjail']
interpreters.cling_bin = config['cling']
interpreters.cling_dir = config['cling-dir']


@bot.event
async def on_ready():
    print('running as {0.user}'.format(bot))


@bot.command()
async def eval(ctx, *, args):
    code_pattern = re.compile(r'`(?P<code>[\S \t]*)`')
    argument_pattern = re.compile(r'-([-a-zA-Z]+)')

    code = code_pattern.search(args)['code']
    arguments = code_pattern.sub(args, '')

    arguments = [x[0] for x in argument_pattern.findall(arguments)]

    stdout, stderr, return_code = interpreters.cling(code, arguments)

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
