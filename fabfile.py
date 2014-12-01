import os

from fabric.api import run, settings, env, cd
from fabric.contrib import files


def local():
    env.hosts = ['localhost']


def update_bootstrap(tag=None):
    """
    Update Bootstrap files to tag version. If a tag isn't specified just
    get latest version.
    """
    repo = 'https://github.com/twitter/bootstrap'
    local_path = os.path.join(os.path.dirname(__file__),
                             'templates/static/less/bootstrap')

    with settings(warn_only=True):
        # Create the source directory if it doesn't exist
        if not files.exists('~/src/'):
            run('mkdir ~/src')

        # Clone the Bootstrap project if we don't have a local copy of the repo
        if not files.exists('~/src/bootstrap'):
            with cd('cd ~/src'):
                run('git clone {0}'.format(repo))

        # Pull down updates
        with cd('~/src/bootstrap'):
            run('git pull origin master')

            # Checkout to tag if specified
            if tag:
                run('git checkout {0}'.format(tag))

            # Remove the project's Bootstrap files
            run('rm -vR {0}'.format(local_path))

            # Copy the updated files into the project
            run('cp -vfR less {0}'.format(local_path))