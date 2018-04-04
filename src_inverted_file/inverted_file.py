# inverted_file.py Custom tf-idf system for the IE bot
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

from sortedcontainers import SortedDict as sd
from sortedcontainers import SortedList

from src_inverted_file.naive_disk_interfacer import NaiveDiskInterfacer as ndi
from src_inverted_file.score import *


class InvertedFile(object):
    """
    Class made to represent an index in memory, with the final purpose of saving and reloading it chunk-by-chunk.
    Initialize :
        - score_function : function of prototype [integer function(token, document)], which will be used to
          compute the part of the score relative to a unique word in a document that will be saved on disc.
          parameters :
              - token : string, a tokenized word expected to be found in a document
              - document : IEMessage, an element of the list <FormattedDocument.matches>, of shape (id, date, length, text) :
                  - id : integer, the id of a message
                  - date : string, when the message is written
                  - length : integer, how many words are in the message
                  - text : List of tokens
          - return:
              - integer, a score relative to a word and an message. Please note that the score is expected to be relative
                to a specific "word", not to "the word XXX at the position XXX". For example, in the message "The black hound ate the
                black bear.", there is a single, unique score relative to the word "black".

    Attributes :
        - __map : SortedDict, the structure used to store the index in memory. Shape (key: string, value: List)
            - key : string, words found in various documents
            - value : list, list of pairs (docid, score) :
                - docid : integer, the id of a document to identify it in the index
                - score : integer, the score computed by __score_function for the association (key, doc)
       - __score_function : the score_function sent in parameter for __init__, memorized by the index (see Initialize/score_function for
         more infos)
    """

    def __init__(self, score_function, disk_interfacer=ndi):
        self.__map = sd()
        self.__score_function = score_function
        self.di = disk_interfacer

    @property
    def map(self):
        """
        Getter for the attribute __map
        :return: SortedDict, a reference to the __map attribute
        """
        return self.__map

    @map.setter
    def map(self, value):
        """
        Setter for the attribute __map, forbidding outside modifications
        """
        pass

    def add_document(self, document):
        """
        Add a message in the data structure.
        :param document : dictionary, an element of the list <FormattedDocument.matches>, of shape (id, title, date, length, text) :
                  - id : integer, the id of a message
                  - date : string, when the message is written
                  - length : integer, how many words are in the message
                  - text : List of tokens
        :return: None
        """
        tokens = document.text.copy()
        seen_list = []
        for token in tokens:
            if token not in seen_list:
                seen_list.append(token)
                computed_score = self.__score_function(token, document)
                if token not in self.__map:
                    self.__map[token] = SortedList()
                self.__map[token].add((document.id, computed_score))

# ---------------------------------------------------------------------------------------------------------------------#
# ---------------------------------------------------------SAVE AND LOAD-----------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------#

    def get_object_as_array(self):
        """
        Used for testing purposes, only encode the object without saving it
        :return: bytearray, a binary representation of the full object
        """
        output = bytearray()
        for (key, value) in self.__map.iteritems():
            output += self.di.encode_posting_list(key, value)
        return output

    def save(self, filename):
        """
        Save the InvertedFile to the disc
        :param filename: string, the path of the inverted file to be saved on disc
        :return: None
        """
        output = bytearray()
        for (key, value) in self.__map.iteritems():
            output += self.di.encode_posting_list(key, value)
        with open(filename, 'wb+')as f:
            f.write(output)

    def read_posting_lists(self, keys, filename):
        """
        Read and decode the posting lists correspoself.ding to their associated keys given in parameters, from a given file.
        Load them into the current object.
        :param keys: list of string, represents the posting lists that need to be decoded
        :param filename: string, the name of the file to read on disc
        :return: None
        """
        with open(filename, 'rb') as f:

            while True:
                key, list_len = self.__read_key_and_list_len(f, self.di)
                if key is None:
                    break
                # if key is one of the wanted keys
                if keys is None or key in keys:
                    posting_list = self.di.decode_list(f.read(list_len))
                    self.__map[key] = posting_list
                else:
                    f.seek(list_len, 1)

    @classmethod
    def read_only_keys(cls, filename, interfacer=ndi):
        """
        Read a binary file and extract only the keys, skipping the reading of their associated posting lists
        :param filename: string, the path of the inverted file to be read on disc
        :return: list of string, where each element is the representation of a keyword
        """
        output = []
        with open(filename, 'rb') as f:

            while True:
                position = f.tell()
                key, list_len = cls.__read_key_and_list_len(f, interfacer)
                if key is None:
                    break
                output.append((key, position))
                f.seek(list_len, 1)

        return output

    @classmethod
    def __read_key_and_list_len(cls, file, interfacer=ndi):
        """
        Read the next few bytes of a binary file and decode them.
        Precoself.dition : The next bytes must represent a key and the length of an associated posting list shaped as :
        <key_size(1 byte)><key(key_size bytes)><list_len(list_len_len bytes)>
        :param file: File, the binary file to read the next bytes in
        :return: a tuple (key, list_len) where :
            - key : string, the key word associated with the next posting list
            - list_len : integer, the length (in bytes) of the next posting list
        """
        # get key
        bin_key_len = file.read(interfacer.key_len_len)
        if len(bin_key_len) != interfacer.key_len_len:
            return None, None
        key_len = interfacer.decode_number(bin_key_len)

        bin_key = file.read(key_len)
        key = bin_key.decode('utf-8')

        # get list len
        bin_list_len = file.read(interfacer.list_len_len)
        list_len = interfacer.decode_number(bin_list_len)

        return key, list_len

    @classmethod
    def __read_key_and_posting_list(cls, file, interfacer=ndi):
        """
        Read the next few bytes of a binary file and decode them.
        Precondition : The next bytes must represent posting list and its associated key shaped as :
        <key_size(1 byte)><key(key_size bytes)><list_len(list_len_len bytes)>( (<doc_id(id_len bytes)><score(score_len bytes)>)*N )
        :param file: File, the binary file to read the next bytes in
        :return: a tuple (key, posting_list) where :
            - key : string, the key word associated with the next posting list
            - posting_list : list, a list of tuples (doc_id, score) where each :
                - doc_id : integer, the unique id of a message
                - score : integer, the score of this message relative to the keyword of this posting list
        """
        key, list_len = cls.__read_key_and_list_len(file, interfacer)
        posting_list = interfacer.decode_list(file.read(list_len))
        return key, posting_list

# ---------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------------MERGE INVERTED FILES-----------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------#

    @classmethod
    def merge_inverted_files(cls, filename_merge, filename_if1, filename_if2, disc_interfacer):
        """
        Merge two inverted files saved on disc into one.
        :param filename_merge: string, the path to the newly created inverted file
        :param filename_if1: string, the path to the first inverted file to merge
        :param filename_if2: string, the path to the second inverted file to merge
        :param disc_interfacer: class, one of NaiveDiscInterfacer and SmartDiscInterfacer, explain the way if1 and if2 are encoded
        :return: None
        """

        with open(filename_merge, 'wb+') as output:
            with open(filename_if1, 'rb') as if1:
                with open(filename_if2, 'rb') as if2:
                    key_if1, pl_if1 = cls.__read_key_and_posting_list(if1)
                    key_if2, pl_if2 = cls.__read_key_and_posting_list(if2)
                    while True:

                        if key_if1 is None and key_if2 is None:
                            break
                        elif key_if1 is not None and (key_if2 is None or key_if1 < key_if2):
                            posting_list = pl_if1
                            key = key_if1
                            key_if1, pl_if1 = cls.__read_key_and_posting_list(if1)
                        elif key_if1 is None or key_if1 > key_if2:
                            posting_list = pl_if2
                            key = key_if2
                            key_if2, pl_if2 = cls.__read_key_and_posting_list(if2)
                        else:
                            posting_list = pl_if1 + pl_if2
                            key = key_if1
                            key_if1, pl_if1 = cls.__read_key_and_posting_list(if1)
                            key_if2, pl_if2 = cls.__read_key_and_posting_list(if2)
                        output.write(disc_interfacer.encode_posting_list(key, posting_list))


def generate_inverted_file(messages):
    from src_inverted_file.formatted_document import FormattedDocument
    from src_inverted_file.tokenizer import Tokenizer
    import time

    time_output_filename = "inverted_file/time.txt"
    with open(time_output_filename, "a+") as time_output:
        time_output.write("\n\n========== Run beginning at " + str(time.time()) + "===========\n")
        inverted_file = InvertedFile(score)
        print("Begin to create inverted file")
        start_time = time.time()
        fd = FormattedDocument(messages=messages, tokenizer=Tokenizer())
        for doc in fd.matches:
            inverted_file.add_document(doc)
        end_time = time.time()

        time_output.write("number of messages : " + str(len(messages)) + ", time : " + str(end_time - start_time) + "\n")
        inverted_file_path = "inverted_file/inverted_file_{}.if".format(str(len(messages)))
        inverted_file.save(inverted_file_path)
        return inverted_file_path
