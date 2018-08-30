import logging
import shutil
import getpass
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

from git import Repo
from git.exc import *

from .exc import *

git_logger = logging.getLogger("git")
git_logger.setLevel(logging.INFO)

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

# Disable logging because too verbose for now.
log.disabled = True
git_logger.disabled = True


class Tibl:
    """
    Represents a tibl instance.
    
    TODO: Separate git and non git code.
          This way, it will be easier to use tibl-cli without git.
          Git code is changes, pull, and push.
  """

    def __init__(self, name):
        """
      Create a tibl instance object to talk with tibl.
      Tries to get git repo if it is present.
      Otherwise, you won't be able to use pull/push feature. 

      :param name: name of the tibl site
    """
        self.name = name

    def new(self, post_type, post_name, title):
        """
          Create a new post and add it to the database

          :param post_type: Item type. Can be post or page.
          :param post_name: File name of the post
          :param title: Title that you'll have on the post listing
      """

        # Check input validity

        # Check if post_type exists
        if post_type not in ["post", "page"]:
            log.error("Invalid post type supplied.")
            raise TiblFormatError("Invalid post type supplied")

        # Check if there's non ascii characters into the post name
        if len(post_name) != len(post_name.encode()):
            log.error("Invalid characters in post name. Please use only ascii.")
            raise TiblFormatError(
                "Invalid characters in post name. Please use only ascii."
            )

        # Check if there's any spaces in the post name
        if " " in post_name:
            log.error("Don't use spaces in post name.")
            raise TiblFormatError("Don't use spaces in post name.")

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
            log.error("File {} already exists.".format(filename))
            raise TiblFileError("File {} already exists.".format(filename))

        # Creating file
        try:
            with open(filename, "w") as f:
                f.write("# {}".format(title))
            log.info("Created item at {}".format(filename))
        except FileNotFoundError as e:
            # echo_err("Could not create post at {}.".format(os.getcwd())
            log.error(
                "Could not create post at {}".format(os.getcwd() + "/" + filename)
            )
            log.error("Ensure that you are at your site root :)")
            raise TiblFileError(
                "Could not create post. Ensure thatyou are at your site root"
            )

        # Updating database
        # TODO: Add at the beginning of the list rather than
        #       at the end ?
        if post_type == "post":

            try:
                with open("data/database.md", "a") as f:
                    f.write(
                        "* [{}](t.html?{}={})\n".format(
                            title, "t" if post_type == "post" else "p", post_name
                        )
                    )
            except FileNotFoundError as e:
                raise TiblFileError(
                    "Could not find database at {}".format(
                        os.getcwd() + "/data/database.md"
                    )
                )
        else:
            log.info("Not updating database since you've created a page")

    def serve(self, port=8080):
        """
          Start a tiny http server that enables the user to 
          visit its site.

          :param port: Port to use. Default is 8080
      """
        server_address = ("localhost", port)
        httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
        log.info("Serving at http://{}:{}".format(*server_address))
        httpd.serve_forever()

    def create(name):
        """
      Create a new instance of tibl on the self.name folder
    """
        if name not in [None, ""]:
            if os.path.exists(name):
                log.error("directory already exists")
                raise FileExistsError

            try:
                Repo.clone_from("https://github.com/Uinelj/tibl", name)
                shutil.rmtree("{}/.git".format(name), ignore_errors=True)
            except GitCommandError as e:
                print(e)
                print("Error {} cloning tibl".format(e.status))
                raise TiblGitError(e, "Error {} cloning tibl".format(e.status))
