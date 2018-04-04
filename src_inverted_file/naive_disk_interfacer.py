# naive_disk_interfacer.py A naive encoder/decoder to store an inverted file
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


class OutOfBoundError(Exception):
    """
    Exception whose vocation is to be thrown when someone try to encode something
    over more bytes than allowed
    """
    pass


class NaiveDiskInterfacer(object):
    """
    Empty class used as namespace for the naive implementation of saving and reading an InvertedFile in binary

    Class Attributes :

        - score_len : integer, the max number of bytes allowed for the encoding of a score
        - id_len : integer, the max number of bytes allowed for the encoding of a docid
        - list_len_len : integer, the max number of bytes allowed for the encoding of the size of a value associated in _map (in bytes)
          Example : if list_len_len = 4, then the maximum size of a list is pow(2, 8*4) -1 bytes
        - key_len_len : integer, the max number of bytes allowed for the encoding of the size of the key (in bytes)

    """

    score_len = 4
    id_len = 6
    list_len_len = 4
    key_len_len = 1
    doc_id_len = 16
    doc_id_len_len = 1

    def __init__(self):
        pass

# ---------------------------------------------------------------------------------------------------------------------#
# ---------------------------------------------------------NAIVE ENCODING----------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------#

    @classmethod
    def _encode_number(cls, number, bin_size):
        """
        Encode an number in binary over an arbitrary number of bytes
        :param number: integer, the number to be binary encoded
        :param bin_size: integer, the number of bytes to encode the number over
        :return: bytearray, a representation of the number encoded
        """
        if number > 2 ** (bin_size * 8):
            raise OutOfBoundError('Number is too long ({} > 2**({} * 8))'.format(number, bin_size))

        offset_max = (bin_size - 1) * 8
        offset_actual = 0
        n_list = []
        while offset_actual <= offset_max:
            tps = [(number >> offset_actual) & 255]
            offset_actual += 8
            n_list = tps + n_list
        output = bytearray(n_list)
        return output

    @classmethod
    def _encode_key(cls, key):
        """
        Encode a string in binary, in the format : <key_size(key_len_len byte)><key(key_size bytes)>
        :param key : string, the key to encode
        :return: bytearray, the string encoded
        """
        output = bytearray(key, 'utf-8')
        len_part = cls._encode_number(len(output), cls.key_len_len)
        output = len_part + output
        return output

    @classmethod
    def _encode_score(cls, score):
        """
        Encode an integer in binary, in the format : <score(score_len bytes)>
        :param score : integer, the number to encode
        :return: bytearray, the number encoded
        """
        return cls._encode_number(score, cls.score_len)

    @classmethod
    def _encode_doc_id(cls, doc_id):
        """
        Encode a string in binary, in the format : <key_size(key_len_len byte)><key(key_size bytes)>
        :param doc_id : string, the uuid to encode
        :return: bytearray, the string encoded
        """
        len_part = cls._encode_number(cls.doc_id_len, cls.doc_id_len_len)
        output = len_part + doc_id.bytes
        return output

    @classmethod
    def _encode_list(cls, map_content):
        """
        Encode a list of (integer docid, integer score) in binary, in the format : 
        <list_len(list_len_len bytes)>( (<doc_id(id_len bytes)><score(score_len bytes)>)*N )
        :param map_content : list, list of tuples (docid, score) where:
                - docid : integer, id of a message
                - score : integer, score of a message relative to some word
        :return: bytearray, the list encoded
        """
        output = bytearray()
        for (doc_id, score) in map_content:
            output += cls._encode_doc_id(doc_id)
            output += cls._encode_score(score)
        list_len = cls._encode_number(len(output), cls.list_len_len)
        output = list_len + output
        return output

    @classmethod
    def encode_posting_list(cls, key, map_content):
        """
        Encode a pair (key, value) in binary, in the format : 
        <key_size(1 byte)><key(key_size bytes)> <list_len(list_len_len bytes)>( (<doc_id(id_len bytes)><score(score_len bytes)>)*N )
        :param key : string, a word, key of the map representing the index
        :param map_content : list, list of tuples (docid, score) where:
                - docid : integer, id of aa message
                - score : integer, score of a message relative to some word
        :return: bytearray, the pair encoded
        """
        return cls._encode_key(key) + cls._encode_list(map_content)

# ---------------------------------------------------------------------------------------------------------------------#
# ---------------------------------------------------------NAIVE DECODING----------------------------------------------#
# ---------------------------------------------------------------------------------------------------------------------#

    @classmethod
    def decode_number(cls, bin_number):
        """
        Convert a binary number into an integer
        :param bin_number: bytearray, binary representation of a number
        :return: integer, unsigned decimal representation of the input number
        """
        int_val = 0
        for octet in bin_number:
            int_val <<= 8
            int_val += octet
        return int_val

    @classmethod
    def _decode_message(cls, bin_message):
        """
        Decode the binary representation of an element of a posting list of shape (doc_id, score)
        :param bin_message: bytearray, the binary representation of an element of a posting list, encoded as
                            <doc_id(id_len bytes)><score(score_len bytes)>
        :return: a tuple (doc_id, score) where :
            - doc_id : integer, the unique id of a message
            - score : integer, the score of this message relative to the keyword of this posting list
        """
        bin_doc_id = bin_message[:cls.id_len]
        bin_score = bin_message[cls.id_len:]
        doc_id = cls.decode_number(bin_doc_id)
        score = cls.decode_number(bin_score)
        return doc_id, score

    @classmethod
    def _bin_message_regenerator(cls, bin_list, size_of_message):
        """
        Generator, cut a binary posting list into separate tuples (doc_id, score) and yield them
        :param bin_list: bytearray, the binary representation of a posting list
        :param size_of_message: integer, the number of bytes it takes to represent a tuple (doc_id, score)
        :return: yield bytearray, the binary representation of an element of the posting list
        """
        cur_index = 0
        while cur_index + size_of_message <= len(bin_list):
            yield bin_list[cur_index:cur_index + size_of_message]
            cur_index += size_of_message
        return

    @classmethod
    def decode_list(cls, bin_list):
        """
        Decode an entire binary posting list of shape : 
        (<doc_id(id_len bytes)><score(score_len bytes)>)*N
        :param bin_list: bytearray, the binary representation of a posting list
        :return: list, a list of tuples (doc_id, score) where each :
            - doc_id : integer, the unique id of a message
            - score : integer, the score of this message relative to the keyword of this posting list
        """
        output = []
        message_gen = cls._bin_message_regenerator(bin_list, cls.id_len + cls.score_len)
        for bin_message in message_gen:
            output.append(cls._decode_message(bin_message))

        return output
