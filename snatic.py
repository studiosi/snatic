import click

from setup.executor import Executor
from setup.requirement_exception import RequirementException
from builder.builder import Builder


@click.group()
def cli():
    pass


@click.command()
def check():
    print("Checking requisites...")
    try:
        Executor.requisites_check()
    except RequirementException as re:
        print(str(re))


@click.command()
def serve():
    Executor.run_command(['php', '-S', 'localhost:8000', '-t', 'site/'])


@click.command()
def build():
    b = Builder()
    b.build()


if __name__ == '__main__':
    cli.add_command(check)
    cli.add_command(serve)
    cli.add_command(build)
    cli()
