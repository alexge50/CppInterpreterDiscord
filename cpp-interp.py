import re
import argparse
import logging

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

logging.basicConfig(
    filename=config['log-file'],
    filemode='w',
    level=logging.DEBUG,
    format='[%(process)d; %(levelname)s] %(asctime)s - %(message)s'
)


@bot.event
async def on_ready():
    logging.info('running as {0.user}'.format(bot))


@bot.command()
async def eval(ctx, *, args):
    code_pattern = re.compile(r'`(?P<code>[\S \t]*)`')
    argument_pattern = re.compile(r'-([-a-zA-Z]+)')

    code = code_pattern.search(args)['code']
    arguments = code_pattern.sub(args, '')

    arguments = [x[0] for x in argument_pattern.findall(arguments)]

    (stdout, stderr, return_code), log_entries = interpreters.cling(code, arguments)



    log_message = \
        f'({ctx.message.author.name}#{ctx.message.author.discriminator} - {ctx.message.author.id})args: {args}\n'
    log_message += '\n'.join([
        str((x.level, x.date.strftime('"%Y-%m-%d, %H:%M:%S'), x.function, x.message)) for x in log_entries
    ])

    logging.info(log_message)

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

    (stdout, stderr, return_code), log_entries = interpreters.cling(code_block, cli_arguments.split(' '))

    log_message = f'args: {args}\n'
    log_message += '\n'.join([
        str((x.level, x.date.strftime('"%Y-%m-%d, %H:%M:%S'), x.function, x.message)) for x in log_entries
    ])

    logging.info(log_message)

    message = f'Return Code: {return_code}\n'

    if stdout is not None:
        message += f'stdout:\n```cpp\n{stdout}\n```'

    if stderr is not None:
        message += f'stderr:\n```fix\n{stderr}\n```'

    await ctx.send(message)


bot.run(config['token'])
