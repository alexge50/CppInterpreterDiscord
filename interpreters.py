import nsjail
from collections import namedtuple

InterpreterOutput = namedtuple('InterpreterOutput', 'stdout stderr return_code')

nsjail_bin = None
cling_bin = None
cling_dir = None


def cling(code, args) -> InterpreterOutput:
    log_entries, executed_program = nsjail.run_process(
        'interpreter-jail.cfg',
        [f'-R{cling_dir}'],
        '/opt/cling/bin/cling',
        code,
        args)

    print(log_entries)

    stdout = executed_program.stdout[177:].strip()
    stderr = executed_program.stderr.strip()

    return InterpreterOutput(
        stdout=None if stdout == '' else stdout,
        stderr=None if stderr == '' else stderr,
        return_code=executed_program.returncode
    )
