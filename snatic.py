import click

from setup.executor import Executor
from setup.requirement_exception import RequirementException
from builder.builder import Builder
from uploader.sftp_uploader import SFTPUploader


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


@click.command()
def upload():
    u = SFTPUploader()
    u.upload()


@click.command()
def deploy():
    b = Builder()
    b.build()
    u = SFTPUploader()
    u.upload()


if __name__ == '__main__':
    cli.add_command(check)
    cli.add_command(serve)
    cli.add_command(build)
    cli.add_command(upload)
    cli.add_command(deploy)
    cli()
