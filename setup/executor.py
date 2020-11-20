import re
import subprocess

from typing import List, NoReturn

from .requirement_exception import RequirementException

EXECUTOR_PHP_TEST_REGEX = r'PHP 7\.'
EXECUTOR_COMPOSER_TEST_REGEX = r'Composer version 2\.'


class Executor:

    @staticmethod
    def execute_command(command: List) -> subprocess.CompletedProcess:
        return subprocess.run(command, capture_output=True, shell=True)

    @staticmethod
    def run_command(command: List) -> NoReturn:
        cmd = " ".join(command)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        # Make port configurable
        print("Development server running -> http://localhost:8000")
        while p.poll() is None:
            out = p.stdout.readline()
            print(out)
        print(p.stdout.read())

    # Checks if PHP is installed and version >= 7.0
    @staticmethod
    def check_php():
        out = Executor.execute_command(['php', '--version'])
        if out.stdout is None:
            return False
        m = re.search(EXECUTOR_PHP_TEST_REGEX, out.stdout.decode('utf-8'))
        return m is not None

    # Checks if Composer is installed and version >= 2.0
    @staticmethod
    def check_composer():
        out = Executor.execute_command(['composer', '-V'])
        if out.stdout is None:
            return False
        m = re.search(EXECUTOR_COMPOSER_TEST_REGEX, out.stdout.decode('utf-8'))
        return m is not None

    # Check if the system requirements are fulfilled
    @staticmethod
    def requisites_check() -> NoReturn:
        if not Executor.check_php():
            raise RequirementException("PHP not on PATH, not installed or version < 7.0")
        else:
            print("PHP >= 7.0 found")
        if not Executor.check_composer():
            raise RequirementException("Composer not on PATH, not installed or version < 2.0")
        else:
            print("Composer >= 2.0 found")
        # TODO: Potentially check if NPM is installed (future)
