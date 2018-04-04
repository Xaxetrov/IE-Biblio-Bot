# tokenizer.py A custom word tokenizer used by the IE bot
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

import nltk

# TODO: "punkt" local caching
nltk.download('punkt')


class Tokenizer:
    """
    Class made to provide better tokenization features than nltk only.
    It can remove punctuation and stem tokens.
    Initialize :
            - punctuation : A list of symbols you want to remove from the tokens if they are found alone.
                Default is ['!', '?', '.', ',', ';', ':', '"', "'", '(', ')', '-', "''", '``']
            - stemming : Whether you want to perform stemming on tokens or not. The method used is Porter's algorithm.
    Attributes :
        - __punctuation : A list of lone symbols to filter from tokens.
        - __stemmer : A chosen stemmer to use.
    """

    def __init__(self, punctuation=['!', '?', '.', ',', ';', ':', '"', "'", '(', ')', '-', "''", '``'], stemming=True):
        self.__punctuation = punctuation
        if stemming:
            self.__stemmer = nltk.stem.porter.PorterStemmer()

    def word_tokenize(self, paragraph):
        """
        - Tokenize the input string to a token list using nltk.world_tokenize
        - Remove single punctuation symbols found in self.__punctuation
        - Try to stem using self.__stemmer. If there is none does nothing instead.
        Parameters :
            - paragraph : The text to process
        Return :
            - a list of tokens
        """
        tokens = nltk.word_tokenize(paragraph)
        tokens = [token for token in tokens if token not in self.__punctuation]

        try:
            tokens = [self.__stemmer.stem(token) for token in tokens]
        except AttributeError:
            # If stemmer is not defined
            pass

        return tokens
