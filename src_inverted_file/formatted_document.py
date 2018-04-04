# formatted_document.py Definition of a document, in the idf meaning of it. Interfaces it with IE messages
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

import json
import nltk

from src_inverted_file.ie_message import IEMessage


class FormattedDocument(object):
    """
    Class made to handle specific parsing of a message list and converting it to a json file tokenized,
    which is easier to interpret
    Initialize :
        - choose one of :
            - messages : list of Message (see class definition)
            - json_doc : initialize from a json string of shape {'document': self.matches}
        - tokenizer : object which must implements a method "word_tokenize", which is then used to
          tokenize the title and text. Default is nltk

    Attributes :
        - matches : a list of elements, where an element represents a message and :
              element : IEMessage (id, date, length, text) :
                - id : integer, the id of an message
                - date : string, when the message is written
                - length : integer, how many words are in the message
                - text : list of string, where each element is a token
        - __tokenizer : the object implementing word_tokenize. Default is nltk
    """

    def __init__(self, messages=None, json_doc=None, tokenizer=nltk):
        if tokenizer == nltk:
            nltk.download('punkt')

        self.__tokenizer = tokenizer
        if messages is not None:
            self.matches = self.__format(messages)
        elif json_doc is not None:
            self.matches = json.loads(json_doc)['document']
        else:
            self.matches = []

    def __format(self, messages):
        """
        convert the xml file into lists and dictionnaries,
        with the advantages of getting rid of useless informations and loading
        it in python containers
        parameters :
            - xml_root_doc : xml.etree.ElementTree, root of an xml document
        return :
            - a list of elements, where an element represents a message and :
              element : dictionary (id, title, date, length, text) :
                - id : integer, the id of a message
                - title : string, the title of the message
                - date : string, when the message is written
                - length : integer, how many words are in the message
                - text : list, a list of string, where each string is a paragraph
        """
        output = []

        for discord_message in messages:
            element = IEMessage()

            # parts that are necessary (id is auto-generated)
            message_text = self.__tokenizer.word_tokenize(discord_message.content)
            element.text = message_text

            # parts that are bonuses
            message_author = discord_message.author
            element.author = message_author

            message_date = discord_message.timestamp
            element.date = message_date

            for attachment in discord_message.embeds:
                element.add_link(attachment["url"])

            output.append(element)
        return output

    def to_json(self):
        """
        Convert the object into a json string
        parameters : None
        return :
            - a string, which is of shape {'document': self.matches}
        """
        return json.dumps({'document': self.matches})

    @staticmethod
    def sum(doc1, doc2):
        """
        append doc1 and doc2 to return a condensed document
        parameters:
            - doc1, doc2: two FormattedDocument to be concatenated
        return :
            - a FormattedDocument, where its attribute self.matches is the concatenation
              of the two first attributes self.matches
        """
        doc3 = FormattedDocument()
        doc3.matches = doc1.matches + doc2.matches
        return doc3
