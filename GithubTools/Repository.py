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

__all__ = [
    'Repository',
]

####################################################################################################

from datetime import datetime

# import numpy as np
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
        elif isinstance(obj, list):
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
