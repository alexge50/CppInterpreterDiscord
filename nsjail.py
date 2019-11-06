import subprocess
import re
from collections import namedtuple
from tempfile import NamedTemporaryFile
import datetime

LogEntry = namedtuple('LogEntry', 'level date function message')
ExecutedProgram = namedtuple('ExecutedProgram', 'stdout stderr returncode')


def run_process(config, command, stdin, args) -> ([LogEntry], ExecutedProgram):
    nsjail_log = NamedTemporaryFile()

    jail_command = [
        'nsjail',
        '--config', config,
        '--log', nsjail_log.name,
        '--verbose',
        '--', command, *args
    ]
    result = subprocess.Popen(jail_command,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).communicate(stdin.encode())

    log_pattern = re.compile(
            r"\[(?P<level>(I)|[DWEF])\]\[(?P<date>.+?)\](?(2)|(?P<function>\[\d+\] .+?:\d+ )) ?(?P<message>.+)")

    log_entries = []
    log_content = nsjail_log.read().decode("utf-8")
    for x in log_content.splitlines():
        match = log_pattern.fullmatch(x)

        if match is not None:
            log_entries.append(
                LogEntry(
                    level=match['level'],
                    date=None if match['date'] is None else datetime.datetime.strptime(match['date'], '%Y-%m-%dT%H:%M:%S%z'),
                    function=match['function'],
                    message=match['message']
                )
            )

    match = re.compile(r"exited with status: (?P<returncode>-?[0-9]+)").search(log_content)
    executed_program = ExecutedProgram(
        stdout=result[0].decode(),
        stderr=result[1].decode(),
        returncode=match['returncode']
    )

    return log_entries, executed_program
