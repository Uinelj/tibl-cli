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
log.disabled = False
git_logger.disabled = True

def git_error(func):
  """
  TODO: Decorator for handling GitCommandErrors 
  If error isn't of type GitCommandError, raise and quit
  If not, print a custom message.
  """
  try:
    func()
  except GitCommandError as e:
    log.warn("Git command failed :(")

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

    # See if a git repo is present, and make it accessible
    # if there's one
    try:
      self.repo = Repo(self.name)
      self.tibl_remote = self.repo.remotes['tibl']
    except InvalidGitRepositoryError as e:
      log.info("No repository at {}".format(name))
      # raise TiblGitError
    except NoSuchPathError as e:
      log.info("Nothing found at {}".format(name))
      raise TiblFileError("Nothing found at {}".format(name))

  def items(self):
    """
      List docs.

      Previous implementation was messy and not better
      than calling `tree`.
    """
    log.info("Not yet implemented.")
    pass
  
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
          log.error(
              "Invalid characters in post name. Please use only ascii."
          )
          raise TiblFormatError("Invalid characters in post name. Please use only ascii.")

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
          log.error("Could not create post at {}".format(
              os.getcwd() + "/" + filename))
          log.error("Ensure that you are at your site root :)")
          raise TiblFileError("Could not create post. Ensure thatyou are at your site root")

      # Updating database
      # TODO: Add at the beginning of the list rather than
      #       at the end ?
      if post_type == "post":
          
          try:
              with open("data/database.md", "a") as f:
                  f.write(
                      "* [{}](t.html?{}={})\n".format(
                          title,
                          "t" if post_type == "post" else "p",
                          post_name,
                      )
                  )
          except FileNotFoundError as e:
              # echo_err("Could not create post at {}.".format(os.getcwd())
              log.error("Could not find database at {}".format(
                  os.getcwd() + "/data/database.md"))
              log.error("Ensure that you are at your site root :)")
              raise TiblFileError("Could not find database at {}".format(
                  os.getcwd() + "/data/database.md"))
      else:
          log.info(
              "Not updating database since you've created a page"
          )
  
  def serve(self, port=8080):
      """
          Start a tiny http server that enables the user to 
          visit its site.

          :param port: Port to use. Default is 8080
      """
      server_address = ('localhost', port)
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
    
  def link(self, url):
    """
      Link instance to a remote git repository

      TODO: Do this better by using GitPython objects rather than
            its direct access to git binary.
      

      :param url: URL of the distant repository
    """
    try:
      self.repo = Repo.init(self.name)
      self.tibl_remote = self.repo.create_remote('tibl', url)

    except GitCommandError as e:
      log.error("Error {} creating tibl remote".format(e.status))
      log.error("{}".format(e.stderr.replace("\n", '')))
      raise TiblGitError(e, "Could not add tibl remote. Check if it doesn't already exist")

  def pull(self):
    """
      Pull changes from tibl remote (master branch)

      TODO: Do this better by using GitPython objects rather than
            its direct access to git binary.
      TODO: Print a nice diff of changes that were imported
    """
    if self.repo.is_dirty():
      log.error("You have unpublished work that's hanging around")
      log.error("You may need to resolve this manually for now :[")
    else:

      # We don't jut do a pull, because if we do and there's conflicts,
      # We'll have to manage those and reset HEAD.
      # Instead, we fetch then merge with --ff-only parameter.
      # See https://adamcod.es/2014/12/10/git-pull-correct-workflow.html
      self.repo.git.fetch('tibl') # Getting branch updates
      self.repo.git.checkout('master') # Be sure that we're on master
      self.repo.git.merge('--ff-only', 'tibl/master')
  
  def push(self):
    """
      Push changes to tibl remote (master branch)

      TODO: Do this better by using GitPython objects rather than
            its direct access to git binary.
      TODO: Print a nice diff of changes that will be pushed
    """

    # Having untracked files is not considered dirty, 
    # So we have to watch for them
    try:
      if self.repo.is_dirty() or len(self.repo.untracked_files) != 0:
        self.repo.index.add(["*"])
        self.repo.index.commit("tibl-cli: update from {}".format(getpass.getuser()))
        self.repo.git.push('tibl', 'master')
      else:
        log.info("Nothing to push")
    except GitCommandError as e:
      raise TiblGitError(e, "Unable to push changes")

  def changes(self):
    """
      Get a list of files that changed since last push
    """
    try:
      print(self.repo.git.status())
    except AttributeError:
      raise TiblGitError("", "Unable to display changes")

def main():
  repo = Tibl("coucou")
  # repo.create()
  # repo.status("https://foo.bar")
  # repo.link("https://gitlab.com/Uinelj/tbtb")
  # repo.changes()
  # repo.pull()
  # repo.new('page', 'zboub ', 'Hi guys !')
  repo.serve()

if __name__ == '__main__':
  main()