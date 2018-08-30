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
        click.echo(ret)


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
    "--post_type", prompt="Item type:", default="post", help="can be post or page."
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
    tibl = Tibl(".")
    try:
        tibl.new(post_type, post_name, title)
    except TiblFileError:
        cli_print(
            "Unable to create {}, ensure that you are in your site's directory".format(
                post_name
            ),
            level="err",
        )
        sys.exit(1)
    except TiblFormatError as e:
        cli_print(e.message, level="err")
        sys.exit(1)
    cli_print("Created {}: {}".format(post_type, post_name))


@cli.command(help="serve your website locally")
@click.option("--port", default=8080, help="server port")
def serve(port):
    """
        Start a tiny http server that enables the user to 
        visit its site.
    """
    tibl = Tibl(".")
    cli_print("Serving on localhost:{}...".format(port))
    tibl.serve(port)


if __name__ == "__main__":

    cli()
