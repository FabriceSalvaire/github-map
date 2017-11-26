####################################################################################################
#
# Copyright (C) 2017 Salvaire Fabrice
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

import json
import os

# http://pygithub.readthedocs.io/en/latest/
from github import Github

from .MarkdownTools import Content
from .Repository import Repository

####################################################################################################

class Repositories:

    ##############################################

    def __init__(self):

        self._github = None
        self._repositories = {}

    ##############################################

    def login(self):

        if self._github is None:
            token_path = os.path.expanduser('~/.github-token')
            with open(token_path, 'r') as f:
                token = f.readline().strip()
                # token = ''

            self._github = Github(login_or_token=token)

    ##############################################

    def _process_repository(self, repository):

        print('  {.name}'.format(repository))

        # http://pygithub.readthedocs.io/en/latest/github_objects/Repository.html
        # https://developer.github.com/v3/repos/
        keys = (
            #! 'topics',
            'created_at',
            'description',
            'fork',
            'forks_count',
            'full_name',
            'html_url',
            'language',
            'name',
            'network_count',
            'private',
            'pushed_at',
            'source',
            'stargazers_count',
            'subscribers_count',
            'updated_at',
            'watchers_count',
        )
        kwargs = {key:getattr(repository, key) for key in keys}

        source = kwargs['source']
        if source is not None:
            kwargs['source'] = source.full_name

        star_dates = []
        if kwargs['stargazers_count']:
            # stargazer.user.login, stargazer.user.name
            star_dates = [stargazer.starred_at
                          for stargazer in repository.get_stargazers_with_dates()]
        kwargs['star_dates'] = star_dates

        repository_data = Repository(**kwargs)
        self._repositories[repository_data.name] = repository_data

    ##############################################

    def upload(self):

        print('Start upload')
        self.login()

        # repository = self._github.get_repo('FabriceSalvaire/CodeReview')
        # self._process_repository(repository)

        for repository in self._github.get_user().get_repos():
            self._process_repository(repository)

        print('Upload done')

    ##############################################

    def save(self, json_path):

        print('Write {}'.format(json_path))
        data = [repository.to_json() for repository in self._repositories.values()]
        print(data)
        with open(json_path, 'w') as fh:
            json.dump(data, fh, indent=4, sort_keys=True)

    ##############################################

    def load(self, json_path):

        print('Load {}'.format(json_path))
        with open(json_path, 'r') as fh:
            data = json.load(fh)
        for repository_data in data:
            repository_data = Repository(**repository_data)
            self._repositories[repository_data.name] = repository_data

    ##############################################

    @property
    def names(self):
        return sorted(self._repositories.keys())

    ##############################################

    def __iter__(self):

        # return iter(self._repositories.values())
        for name in self.names:
            repository = self._repositories[name]
            yield repository

    ##############################################

    def __getitem__(self, name):
        return self._repositories[name]

    ##############################################

    @property
    def forks(self):

        for repository in self:
            if repository.fork:
                yield repository

    ##############################################

    @property
    def fork_names(self):

        for repository in self.forks:
            yield repository.name

    ##############################################

    def by_star(self, names):

        repositories = [self._repositories[name] for name in sorted(names)]
        get_key = lambda x: x.stargazers_count # '{:3}{}'.format(x.stargazers_count, x.name)
        return sorted(repositories, key=get_key, reverse=True)

    ##############################################

    def to_markdown(self, names):

        return ''.join([repository.to_markdown() for repository in self.by_star(names)])

    ##############################################

    def missed(self):

        for repository in self:
            if not repository.listed:
                yield repository

