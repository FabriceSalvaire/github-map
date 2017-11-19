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

from datetime import datetime
import json
import os

# http://pygithub.readthedocs.io/en/latest/
from github import Github

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

####################################################################################################

class Repository:

    ##############################################

    def __init__(self, **kwargs):

        self._keys = kwargs.keys()
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.listed = False

    ##############################################

    @classmethod
    def _python_to_json(cls, obj):

        if isinstance(obj, datetime):
            return str(obj)
        if isinstance(obj, list):
            return [cls._python_to_json(item) for item in obj]
        else:
            return obj

    ##############################################

    @classmethod
    def str_to_datetime(cls, date_string):

        return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

    ##############################################

    def to_json(self):

        return {key:self._python_to_json(getattr(self, key))
                for key in self._keys}

    ##############################################

    def to_markdown(self):

        self.listed = True

        content = '\n'
        content += '* [{0.name}]({0.html_url})'.format(self)
        if self.stargazers_count:
            content += ' {0.stargazers_count} :star:</br>'.format(self)
        content += '\n\n'
        content += '   {0.description}\n\n'.format(self)
        date = self.str_to_datetime(self.updated_at).strftime('%Y-%m-%d')
        content += '   Updated on {}\n'.format(date)

        # {0.language}</br>
        # content += '\n'

        return content

    ##############################################

    @classmethod
    def star_figure(cls, figure_id):

        figure = plt.figure(figure_id, (20, 10))
        axe = plt.subplot(111)
        axe.grid()
        axe.set_title('Star count over time')

        return figure, axe

    ##############################################

    @classmethod
    def save_figure(cls, figure, name):

        image_path = os.path.join('star-plots', name + '.png')
        print('write', image_path)
        figure.savefig(image_path, bbox_inches='tight')

    ##############################################

    def plot_stars(self, axe=None):

        if not self.stargazers_count:
            return

        datetimes = [self.str_to_datetime(x) for x in self.star_dates]
        dates = matplotlib.dates.date2num(datetimes)
        counts = range(1, len(dates) +1)

        new_plot = axe is None
        if new_plot:
            figure, axe = self.star_figure(2)
            axe.set_ylim(0, (counts[-1] // 10) * 10 + 10)

        axe.plot_date(dates, counts, 'o-')

        if new_plot:
            self.save_figure(figure, self.name)
            # plt.show()
            plt.clf()

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

####################################################################################################

class Content:

    ##############################################

    def __init__(self, repositories):

        self._repositories = repositories
        self._content = ''

    ##############################################

    def __iadd__(self, content):

        self._content += content
        return self

    ##############################################

    def __str__(self):

        return str(self._content)

    ##############################################

    def _title(self, level, title):
        self._content += '\n{} {}\n'.format('#'*level, title)

    ##############################################

    def h1(self, title):
        self._title(1, title)

    ##############################################

    def h2(self, title):
        self._title(2, title)

    ##############################################

    def h3(self, title):
        self._title(3, title)

    ##############################################

    def list(self, names):

        self += self._repositories.to_markdown(names)
