# log_vcs - create (git) branch for every ansible run

This callback plugin creates a VCS branch every time you run Ansible. If you ever need to go back to a certain state or environment, check out that branch and be sure nothing has changed.

This is useful when you have multiple environments or multiple people deploying and continually develop your Ansible. When you often deploy to test / acceptance and less often to production, you can checkout the last branch that deployed to production if a hotfix or other maintenance is required, without having to search back in your commits and logs. I would recommend to develop infrastructure features in feature branches and have the master branch always deployable to production. However, reality learns that that is not always the case and this is a nice automatic way to have a fallback.

## Requirements and installation

The plugin requires 'GitPython'. On Ubuntu this can be installed with the package manager:

	apt-get install python-git python3-git

The plugin requires the Ansible folder to be a git repository. If you have a seperate 'roles' directory, that is not included in this plugin. 

More infor can be [found here](https://raymii.org/s/software/log_vcs_-_Ansible_Callback_plugin_that_creates_git_branches_for_every_ansible_run.html)

To install the plugin, create a folder in your Ansible folder: 

	mkdir -p plugins/callbacks

Place the file in there and edit your `ansible.cfg` file:

	[defaults]
	callback_whitelist = log_vcs
	callback_plugins = plugins/callbacks

## Environments

If you have multiple environments (multiple inventories) then every inventory needs a `group_var` (in `group_vars/all.yml`) named `environment`. The plugin uses this in the branch name. In my case it can be `dev`, `tst`, `acc`, `prd` or `mgmt`. It is not required, if it is not found the plugin will substitute it with `env`.

## Branch name format

The branch name format is:

		auto-$year$month$dayT$hour$minute-$env-$branch-$username-$playbook-filename

For example:

	  auto-20180710T100719-env-master-remy-nginx-vps-for-raymii.org.yml

or:

	auto-20180709T161235-tst-refactor-for-odoo-remy-odoo.yml
	auto-20180710T091419-prd-refactor-for-odoo-remy-ping.yml


## Auto-commit or cleanup?

There is no auto-commit or auto-push to a git server. In my use-case deployment is always done from a management machine, otherwise you have to extend the plugin to do auto-commit and push. I decided in my case it would not be useful.

Auto-cleanup is also not implemented. We have bash for that:

	git branch | grep 'auto-' | xargs -L 1 -I % git branch -d %