from __future__ import (absolute_import, print_function, division)
import copy

import six

from . import basetypes, utils


class ODict(basetypes.Serializable):

    """
        A dictionary-like object for managing ordered (key, value) data. Think
        about it as a convenient interface to a list of (key, value) tuples.
    """

    def __init__(self, lst=None):
        self.lst = lst or []

    def _kconv(self, s):
        return s

    def __eq__(self, other):
        return self.lst == other.lst

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        return self.lst.__iter__()

    def __getitem__(self, key):
        """
            Returns a list of values matching key.
        """

        key = self._kconv(key)
        return [
            v
            for k, v in self.lst
            if self._kconv(k) == key
        ]

    def keys(self):
        return list(
            set(
                self._kconv(k) for k, _ in self.lst
            )
        )

    def __len__(self):
        """
            Total number of (key, value) pairs.
        """
        return len(self.lst)

    def __setitem__(self, k, valuelist):
        """
            Sets the values for key k. If there are existing values for this
            key, they are cleared.
        """
        if isinstance(valuelist, six.text_type) or isinstance(valuelist, six.binary_type):
            raise ValueError(
                "Expected list of values instead of string. "
                "Example: odict[b'Host'] = [b'www.example.com']"
            )
        kc = self._kconv(k)
        new = []
        for i in self.lst:
            if self._kconv(i[0]) == kc:
                if valuelist:
                    new.append([k, valuelist.pop(0)])
            else:
                new.append(i)
        while valuelist:
            new.append([k, valuelist.pop(0)])
        self.lst = new

    def __delitem__(self, k):
        """
            Delete all items matching k.
        """
        k = self._kconv(k)
        self.lst = [
            i
            for i in self.lst
            if self._kconv(i[0]) != k
        ]

    def __contains__(self, key):
        key = self._kconv(key)
        return any(
            self._kconv(k) == key
            for k, _ in self.lst
        )

    def add(self, key, value, prepend=False):
        if prepend:
            self.lst.insert(0, [key, value])
        else:
            self.lst.append([key, value])

    def get(self, k, d=None):
        if k in self:
            return self[k]
        else:
            return d

    def get_first(self, k, d=None):
        if k in self:
            return self[k][0]
        else:
            return d

    def items(self):
        return self.lst[:]

    def copy(self):
        """
            Returns a copy of this object.
        """
        lst = copy.deepcopy(self.lst)
        return self.__class__(lst)

    def extend(self, other):
        """
            Add the contents of other, preserving any duplicates.
        """
        self.lst.extend(other.lst)

    def __repr__(self):
        return repr(self.lst)

    def replace(self, pattern, repl, *args, **kwargs):
        """
            Replaces a regular expression pattern with repl in both keys and
            values.

            Returns the number of replacements made.
        """
        new, count = [], 0
        for k, v in self.lst:
            k, c = utils.safe_subn(pattern, repl, k, *args, **kwargs)
            count += c
            v, c = utils.safe_subn(pattern, repl, v, *args, **kwargs)
            count += c
            new.append([k, v])
        self.lst = new
        return count

    # Implement Serializable
    def get_state(self):
        return [tuple(i) for i in self.lst]

    def set_state(self, state):
        self.lst = [list(i) for i in state]

    @classmethod
    def from_state(cls, state):
        return cls([list(i) for i in state])


class ODictCaseless(ODict):

    """
        A variant of ODict with "caseless" keys. This version _preserves_ key
        case, but does not consider case when setting or getting items.
    """

    def _kconv(self, s):
        return s.lower()
