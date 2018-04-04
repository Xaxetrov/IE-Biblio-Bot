# ie_message.py Definition of a message used by the custom tf-idf of the bot
#
# Copyright (C) 2017-2018 Edern Haumont, Jérome Liermann, François Robion, Nicolas Six
#
# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file LICENSE.  If not see
# <http://www.gnu.org/licenses/>.

import uuid


# TODO change attributes to property style : https://www.python-course.eu/python3_properties.php
class IEMessage(object):
    def __init__(self):
        self.__author = ""
        self.__date = None
        self.__id = uuid.uuid1()
        self.__links = []
        self.__text = []
        self.__length = len(self.__text)

    @property
    def author(self):
        return self.__author

    @property
    def date(self):
        return self.__date

    @property
    def id(self):
        return self.__id

    @property
    def length(self):
        return self.__length

    @property
    def link(self):
        return self.__link

    @property
    def text(self):
        return self.__text

    @author.setter
    def author(self, val):
        self.__author = val

    @author.setter
    def date(self, val):
        self.__date = val

    @text.setter
    def text(self, val):
        self.__text = val
        self.__length = len(self.__text)

    def add_link(self, link):
        self.__links.append(link)
