import logging
import os
import http.server
import socketserver
import subprocess

import click
import crayons as c
import blindspin

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("tibl")


def echo_good(string, prefix="🗿"):
    """
        Prints out in green.

        :param string: String to print
        :param prefix: String to put at the left,
                       to emulate hipster nodejs apps
    """
    click.echo(c.green(prefix + " " + string))


def echo_warn(string, prefix="🗿"):
    """
        Prints out in yellow.

        :param string: String to print
        :param prefix: String to put at the left,
                       to emulate hipster nodejs apps
    """
    click.echo(c.yellow(prefix + " " + string))


def echo_err(string, prefix=""):
    """
        Prints out in red.

        :param string: String to print
        :param prefix: String to put at the left,
                       to emulate hipster nodejs apps
    """
    click.echo(c.red(prefix + " " + string))


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
    click.echo("Cloning tibl...")

    with blindspin.spinner():
        clone_result = subprocess.run(
            [
                "git",
                "clone",
                "https://github.com/Uinelj/tibl.git",
                name,
                "-q",
            ],
            stdout=subprocess.PIPE,
        )

        # Check if all went good
        if clone_result.returncode != 0:
            echo_err("Something went wrong when cloning tibl")
        else:
            echo_good("it's all gucci")


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

    # Check input validity

    # Check if post_type exists
    if post_type not in ["post", "page"]:
        echo_err("Invalid post type supplied.")
        return

    # Check if there's non ascii characters into the post name
    if len(post_name) != len(post_name.encode()):
        echo_err(
            "Invalid characters in post name. Please use only ascii."
        )
        return

    # Check if there's any spaces in the post name
    if " " in post_name:
        echo_err("Don't use spaces in post name.")
        return

    # End of check

    # Add markdown extention
    filename = post_name + ".md"

    # add a _ to separate pages and posts
    if post_type == "page":
        filename = "_" + filename

    # Add path to topics
    filename = "data/topics/" + filename

    # Check if file exists
    if os.path.isfile(filename):
        echo_err("File {} already exists.".format(filename))
        return

    # Creating file
    with open(filename, "w") as f:
        f.write("# {}".format(title))
    click.echo(echo_good("Created item at {}".format(filename)))

    # Updating database
    # TODO: Add at the beginning of the list rather than
    #       at the end ?
    if post_type == "post":
        with open("data/database.md", "a") as f:
            f.write(
                "* [{}](t.html?{}={})\n".format(
                    title,
                    "t" if post_type == "post" else "p",
                    post_name,
                )
            )
    else:
        echo_warn(
            "Not updating database since you've created a page"
        )


@cli.command(help="list posts and pages")
def items():
    echo_warn("database.md support is experimental af")

    items = os.listdir("data/topics")
    pages = [item for item in items if item.startswith("_")]
    posts = [item for item in items if item not in pages]

    postlist = {}

    # Open the post list
    # And get post listing (lines that are * [blahblah]())
    # TODO: This is very ugly.
    with open("data/database.md", "r") as dbfile:

        # Go from * [foo](t.html?p=bar)
        # To {title:'foo', 'filename':_bar.md}
        for line in dbfile.readlines():
            if "* [" in line:
                # * [foo](t.html?p=bar)
                line = line.replace("* [", "")
                line = line.replace(")\n", "")

                # foo]t.html?p=bar)
                title, filename_and_type = line.split(
                    "](t.html?", 2
                )

                # title:foo, filename_and_type:p=bar

                item_type, filename = filename_and_type.split("=")

                if item_type == "t":
                    pass
                elif item_type == "p":
                    filename = "_" + filename
                else:
                    echo_err(
                        "There's a problem in this link : {}".format(
                            line
                        )
                    )
                postlist[filename + ".md"] = title

    # List pages
    click.echo("\nPages:")
    click.echo("------")
    for item in pages:
        click.echo(
            c.yellow("  - data/topics/{}".format(item), bold=True)
        )

    # List posts
    # Display title if in database
    click.echo("\nPosts (Path -> Title):")
    click.echo("------")

    # We try to get the item from the postlist
    # If we can't, we format in red
    for item in posts:
        fmt = "  - data/topics/{} -> {}"
        try:
            title = postlist[item]
        except KeyError:
            fmt = c.red(fmt.format(item, ""), bold=True)
        else:
            fmt = c.green(fmt.format(item, title), bold=True)
        click.echo(fmt)

    click.echo("")


def clean():
    pass


def pull():
    pass


def push():
    pass


def update():
    pass


@cli.command(help="serve your website locally")
@click.option("--port", default=8080, help="server port")
def serve(port):
    """
        Start a tiny http server that enables the user to 
        visit its site.
    """
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), Handler) as httpd:
        echo_good(
            "Your site lives here : http://localhost:{}".format(
                port
            )
        )
        httpd.serve_forever()


if __name__ == "__main__":
    cli()
