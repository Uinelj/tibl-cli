import logging
import sys

import click
import blindspin
import crayons

from .tibl import Tibl
from .exc import *

def cli_print(string, level="ok", prefix="🗿", bold=False):
    ret = prefix + " " + string
    if level == "ok":
        click.echo(crayons.green(ret, bold=bold))
    elif level == "wrn":
        click.echo(crayons.yellow(ret, bold=bold))
    elif level == "err":
        click.echo(crayons.red(ret, bold=bold))
    elif level == "dbg":
        click.echo(crayons.magenta(ret, bold=bold))
    else:
        click.echo("Wrong color m8")

@click.group()
def cli():
    pass

@cli.command(help="Create a new tibl site")
@click.option("--name", prompt="Site directory")
def create(name):
    """
        Clone the master branch of tibl into the specified folder.

        :param name: Name of the folder. 
                     Should work with directories.
    """
    ret = ""
    click.echo("Creating tibl site...")
    with blindspin.spinner():
        try:
            Tibl.create(name)
        except FileExistsError as e:
            cli_print("directory {} already exists".format(name), level="err")
            sys.exit(1) 
    cli_print("tibl site {} created !".format(name), level="ok")
    sys.exit(0)

@cli.command(help="Create a new post/page")
@click.option(
    "--post_type",
    prompt="Item type:",
    default="post",
    help="can be post or page.",
)
@click.option(
    "--post_name",
    prompt="File name: ",
    default="hello",
    help="don't use spaces or non-ascii characters",
)
@click.option(
    "--title",
    prompt="Item title: ",
    default="Hi",
    help="this will be the title of your new item",
)
def new(post_type, post_name, title):
    """
        Create a new post and add it to the database

        :param post_type: Item type. Can be post or page.
        :param post_name: File name of the post
        :param title: Title that you'll have on the post listing
    """
    tibl = Tibl('.')
    try:
        tibl.new(post_type, post_name, title)
    except TiblFileError:
        cli_print("Unable to create {}, ensure that you are in your site's directory".format(post_name), level="err")
        sys.exit(1)
    except TiblFormatError as e:
        cli_print(e.message, level="err")
        sys.exit(1)
    cli_print("Created {}: {}".format(post_type, post_name))


@cli.command(help="list posts and pages")
def items():
    cli_print("items has been deactivated because it worked bad.", level="wrn")
    cli_print("Use tree data/, sorry", level="wrn")
    pass


@cli.command(help="link a github repository")
@click.option(
    "--url", prompt="GitHub URL:", help="Github URL of your repo"
)
def link(url):
    tibl = Tibl('.')
    try:
        tibl.link(url)
    except TiblGitError as e:
        # cli_print("Unable to link with repository {}".format(url), level="err")
        cli_print(e.message, level="err")
        sys.exit(1)
    cli_print("Linked with repository {}".format(url))

@cli.command(help="Push changes to a github repository")
@click.option(
    "--only-data",
    default=False,
    help="Only push data/ folder. Default is false",
)
def push(only_data):
    tibl = Tibl('.')
    try:
        tibl.push()
    except TiblGitError:
        cli_print("Error trying to push changes to remote repository", level="err")
        sys.exit(1)
    cli_print("Pushed changes to remote repository", level="warn")

@cli.command(help="Pull changes from a github repository")
def pull():
    tibl = Tibl('.')
    try:
        tibl.push()
    except TiblGitError:
        cli_print("Error trying to pull changes from remote repository", level="err")
        sys.exit(1)
    cli_print("Pulled changes from remote repository", level="warn")

@cli.command(help="Print out current changes")
def changes():
    tibl = Tibl('.')
    try:
        tibl.changes()
    except TiblGitError:
        cli_print("Check that git is properly initialized in your directory", level="wrn")
        sys.exit(1)

def update():
    pass


@cli.command(help="serve your website locally")
@click.option("--port", default=8080, help="server port")
def serve(port):
    """
        Start a tiny http server that enables the user to 
        visit its site.
    """
    tibl = Tibl('.')
    cli_print("Serving on localhost:{}...".format(port))
    tibl.serve(port)
if __name__ == "__main__":

    cli()
