# -*- coding: UTF-8 -*-
"""Module for enhancing random preimport.

"""
import operator
import random
import struct
from binascii import hexlify, unhexlify
from ..helpers.data.types import *


class __Base(object):
    """ Class holding some common methods for other classes of this module """
    def next_block(self, output_format="str", update=False):
        """
        Get the next 32bits-block of data.
        
        :param output_format: output format (string, hexadecimal or binary)
        :param update:        update the state of the generator
        """
        update = self.update or update
        return self.next_blocks(1, output_format, update)

    def next_blocks(self, n, output_format="str", update=False):
        """
        Get the n next 32bits-blocks of data.
        
        :param n:             number of blocks of n bits to be generated after the target (from start if target is None)
        :param output_format: output format (string, hexadecimal or binary)
        :param update:        update the state of the generator
        """
        update = self.update or update
        l = len(getattr(self, "target", None) or "")
        s = self.get(l + n * self.n, output_format, update)
        if output_format == "str":
            return s[l//8:]
        elif output_format == "hex":
            return s[l//4:]
        return s[l:]


class Geffe(__Base):
    """
    Geffe generator class.
    
    This can be defined by its key (12-chars string or 96 bits) or by a tuple of 3 seeds for its internal LFSR.

    :param key:    12-chars key or str/list of 96 bits
    :param seeds:  3-int tuple (or list) with the seeds for the LFSR
    :param update: update the state of the generator when bits are generated

    Example usage:

      >>> from tinyscript import *
      >>> g = random.Geffe("a_12bits_key")
      >>> print(g.next_block())
    """
    n = 32
    taps = [
        (3, 4, 6, 7, 8, 9, 11, 32),
        (1, 2, 3, 4, 6, 8, 9, 13, 14, 32),
        (1, 2, 3, 7, 12, 14, 15, 32),
    ]
    
    def __init__(self, key=None, seeds=(0, 0, 0), update=False):
        seeds = Geffe.format_param(key, seeds)
        self._lfsrs = [LFSR(s, t, 32) for s, t in zip(seeds, Geffe.taps)]
        self.target = self._lfsrs[0].target
        self.update = update
    
    def get(self, length=None, output_format="str", update=False):
        """
        Get a given number of bits from the Geffe generator with the given output format.
        
        :param length:        number of bits to be generated
        :param output_format: output format (string, hexadecimal or binary)
        :param update:        update the state of the generator
        """
        update = self.update or update
        if output_format not in ["str", "hex", "bin"]:
            raise ValueError("Bad output format")
        stream = []
        for bits in zip(self._lfsrs[0].get(length, "bin", update), self._lfsrs[1].get(length, "bin", update),
                        self._lfsrs[2].get(length, "bin", update)):
            stream.append(Geffe.F(*bits))
        if output_format == "str":
            return bin2str(stream)
        elif output_format == "hex":
            return hexlify(bin2str(stream))
        else:
            return stream
        
    @staticmethod
    def F(x1, x2, x3):
        return (x1 & x2) ^ (int(not x1) & x3)
    
    @staticmethod
    def format_param(key, seeds):
        if key is not None:
            l, err = len(key), "Bad key format ({})"
            if is_str(key):
                if l == 12:
                    seeds = struct.unpack("iii", key)
                elif l == 96 and is_bin(key):
                    seeds = tuple([bin2int(key[i:i+32]) for i in \
                                   range(0, 96, 32)])
            elif is_list(key):
                if l == 3 and all(is_str(s) for s in key):
                    seeds = tuple(map(lambda s: struct.unpack("i", s), key))
                elif l == 96 and is_bin(key):
                    bits = ''.join(list(map(str, key)))
                    seeds = map(lambda x: int("0b" + x, 2), \
                                [bits[i:i+32] for i in range(0, 96, 32)])
        if len(seeds) != 3 or any(not is_pos_int(i) or i.bit_length() > 32 for i in seeds):
            raise ValueError("Invalid seeds")
        return seeds


class LFSR(__Base):
    """
    Linear Feedback Shift Register (LFSR) class.
    
    This can be defined by its parameters (seed, taps, nbits) or can be determined from a target using the
     Berlekamp-Massey algorithm.

    :param seed:   integer, list of bits or string for initializing the LFSR
    :param taps:   tuple or list of indices of the polynomial
    :param nbits:  LFSR register length of bits
    :param target: input string or list of bits to be matched while determining LFSR's parameters
    :param update: update the state of the LFSR when bits are generated

    Example usage:

      >>> from tinyscript import *
      >>> l = random.LFSR("0123456789abcdef")
      >>> print(l.next_block())
    """
    def __init__(self, seed=0, taps=None, nbits=None, target=None, update=False):
        if any(x is None for x in [seed, taps, nbits]) and target is None:
            raise ValueError("Either (seed, taps, nbits) or target must be set")
        self.target = target
        if target is not None and (taps is None or nbits is None):
            self.target = LFSR.format_target(target)
            self.__berlekamp_massey_algorithm()
        else:
            self.seed, self.taps, self.n = LFSR.format_param(seed, taps, nbits)
            self.target = [b for b in self.seed]
        # test if parameters are correct
        self.test()
        self.update = update
    
    def __berlekamp_massey_algorithm(self):
        """
        Berlekamp-Massey algorithm for finding the shortest LFSR for a given binary output sequence.
         
        See: https://en.wikipedia.org/wiki/Berlekamp%E2%80%93Massey_algorithm
        """
        bs = list(map(int, [b for b in self.target]))
        n = len(bs)
        b, c = [0 for i in range(n)], [0 for i in range(n)]
        b[0], c[0] = 1, 1
        l, m, i = 0, -1, 0
        while i < n:
            v = bs[(i - l):i]
            v = v[::-1]
            cc = c[1:l + 1]
            d = (bs[i] + sum(map(operator.mul, v, cc))) % 2
            if d == 1:
                _ = [x for x in c]
                p = [0 for i in range(n)]
                for j in range(0, l):
                    if b[j] == 1:
                        p[j + i - m] = 1
                c = (c + p) % 2
                if l <= 0.5 * i:
                    l = i + 1 - l
                    m = i
                    b = _
            i += 1
        c = [i for i, x in enumerate(c) if x == 1]
        c.remove(0)
        self.seed, self.taps, self.n = LFSR.format_param(self.target[:l], c, l)
    
    def get(self, length=None, output_format="str", update=False):
        """
        Get a given number of bits from the LFSR with the given output format.
        
        :param length:        number of bits to be generated
        :param output_format: output format (string, hexadecimal or binary)
        :param update:        update the state of the generator
        """
        if output_format not in ["str", "hex", "bin"]:
            raise ValueError("Bad output format")
        length = length or (1 if self.target is None else len(self.target))
        stream = [b for b in self.seed]
        # generate length - nbits (from the starting stream) bits
        for _ in xrange(length - self.n):
            bit = 0
            for tap in self.taps:
                bit ^= stream[-tap]
            stream.append(bit)
        # update state if required
        if update:
            self.seed = stream[-self.n:]
            self.target = [b for b in self.seed]
        # now format the output according to output_format
        if output_format == "str":
            return bin2str(stream)
        elif output_format == "hex":
            return hexlify(bin2str(stream))
        return stream
    
    def test(self, target=None):
        target = target or self.target
        if self.target is None:
            raise ValueError("Target not defined")
        target = LFSR.format_target(target)
        if target != self.get(len(target), output_format="bin"):
            raise ValueError("Target and generated bits do not match")
    
    @staticmethod
    def format_param(seed, taps, nbits):
        """ Ensure that:
            - seed is formatted as a list of bits
            - taps is a list of integers <= nbits
            - nbits is an integer """
        if isinstance(seed, int):
            seed = int2bin(seed, nbits)
        elif is_str(seed) and not is_bin(seed):
            if is_hex(seed):
                seed = unhexlify(seed)
            seed = str2bin(seed)
        seed = [int(b) for b in seed]
        if not is_bin(seed):
            raise ValueError("Bad input format for seed")
        if not is_pos_int(nbits):
            raise ValueError("Bad input format for number of bits")
        if not is_list(taps) or any(not is_pos_int(i) or i > nbits for i in taps):
            raise ValueError("Bad input format for taps")
        return seed, taps, nbits
    
    @staticmethod
    def format_target(target):
        """ Ensure that target is formatted as a list of bits """
        if is_str(target) and not is_bin(target):
            if is_hex(target):
                target = unhexlify(target)
            target = [int(b) for b in str2bin(target)]
        if not is_bin(target):
            raise ValueError("Bad input format for target")
        return target


random.Geffe = Geffe
random.LFSR  = LFSR

