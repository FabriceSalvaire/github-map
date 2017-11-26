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

__all__ = [
    'Content',
]

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
