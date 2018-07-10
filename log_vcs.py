# (C) 2018 Remy van Elst, https://raymii.org
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: log_vcs
    type: notification
    short_description: create VCS entry for playbook run
    version_added: historical
    description:
      - This plugin creates a VCS entry for playbook runs. 
      - "For example, a git branch for every execution."
      - "This way the exact state can be 're-played'. "
      - "Usefull when working with multiple environments (DTAP) and multiple people,"
      - "where when you are developing your Ansible, you sometimes need to go back"
      - "to a previous point in time and re-run the exact state."
      - "This pluging creates a git-branch for every run, then goes back to the active branch."
      - "TODO: Implement other VCS systems then git."
    requirements:
     - Ansible folder must be git repository
     - Gitpython
'''

import os
import pwd
import sys
import time
from collections import MutableMapping
from ansible.plugins.callback import CallbackBase

# TODO: Implement SVN
try:
    from git import Repo
except ImportError as e:
    print("Please install gitpython.")
    raise e

class CallbackModule(CallbackBase):
    """
    Creates VCS entry for every execution.
    Git only for now, git branch
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'version_history'
    CALLBACK_NAME = 'log_vcs'
    CALLBACK_NEEDS_WHITELIST = True
    TIME_FORMAT = "%Y%m%dT%H%M%S"
    
    def __init__(self):
        super(CallbackModule, self).__init__()
        self.play = None
        if not os.path.exists(os.getcwd() + "/.git/"):
            raise Exception(os.getcwd() + " is not a git repository.")
            sys.exit(1)

    def create_git_branch(self,env_name="env", playbook_filename="playbook.yml"):
        repo = Repo(os.getcwd())
        active_branch = str(repo.active_branch)
        current_datetime = str(time.strftime(self.TIME_FORMAT, time.localtime()))
        current_user = str(pwd.getpwuid(os.geteuid()).pw_name)
        BRANCH_NAME = ("auto-" + current_datetime + "-" + str(env_name) + 
            "-" + active_branch + "-" + current_user + "-" + 
            str(playbook_filename))
        repo.git.checkout('-b', BRANCH_NAME)
        self._display.display("Created branch " + BRANCH_NAME)
        repo.git.checkout(active_branch)

    def playbook_on_play_start(self, play):
        self.v2_playbook_on_play_start(play)

    def v2_playbook_on_play_start(self, play):
        self.play = play
        # every environment has an env var named "environment"
        # with for example "tst", "acc", "prd"
        playbook_path = list(self.play._loader._FILE_CACHE)[0]
        playbook_filename = os.path.basename(playbook_path)
        first_hostname=str(list(self.play._variable_manager._hostvars)[0])
        try:
            env_name=self.play._variable_manager._hostvars[first_hostname]["environment"]
        except Exception as e:
            env_name="env"
        self.create_git_branch(env_name=env_name, playbook_filename=playbook_filename)
