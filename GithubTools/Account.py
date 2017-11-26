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

import os

# http://pygithub.readthedocs.io/en/latest/
from github import Github

####################################################################################################

class Account:

    ##############################################

    def __init__(self):

        self._github = None

    ##############################################

    def login(self):

        if self._github is None:
            token_path = os.path.expanduser('~/.github-token')
            with open(token_path, 'r') as f:
                token = f.readline().strip()
                # token = ''

            self._github = Github(login_or_token=token)

    ##############################################

    @property
    def github(self):
        return self._github
