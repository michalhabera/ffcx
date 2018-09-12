# -*- coding: utf-8 -*-
# Copyright (C) 2011-2017 Martin Sandve Alnæs
#
# This file is part of FFC (https://www.fenicsproject.org)
#
# SPDX-License-Identifier:    LGPL-3.0-or-later
"""Compressed row storage 'matrix' (actually just a non-rectangular 2d array)."""

import numpy


def sufficient_int(maxval):
    return numpy.int16 if maxval < 2**15 else numpy.int32


class CRSArray(object):
    """An array of variable length dense arrays.

    Stored efficiently with simple compressed row storage.
    This CRS array variant doesn't have a sparsity pattern,
    as each row is simply a dense vector.

    Values are stored in one flat array 'data[]',
    and 'row_offsets[i]' contains the index to the first
    element on row i for 0<=i<=num_rows.
    There is no column index.
    """

    def __init__(self, row_capacity, element_capacity, dtype):
        itype = sufficient_int(element_capacity)
        self.row_offsets = numpy.zeros(row_capacity + 1, dtype=itype)
        self.data = numpy.zeros(element_capacity, dtype=dtype)
        self.num_rows = 0

    def push_row(self, elements):
        a = self.row_offsets[self.num_rows]
        b = a + len(elements)
        self.data[a:b] = elements
        self.num_rows += 1
        self.row_offsets[self.num_rows] = b

    @property
    def num_elements(self):
        return self.row_offsets[self.num_rows]

    def __getitem__(self, row):
        if row < 0 or row >= self.num_rows:
            raise IndexError("Row number out of range!")
        a = self.row_offsets[row]
        b = self.row_offsets[row + 1]
        return self.data[a:b]

    def __len__(self):
        return self.num_rows

    def __str__(self):
        return "[%s]" % ('\n'.join(str(row) for row in self), )

    @classmethod
    def from_rows(cls, rows, num_rows, num_elements, dtype):
        """Construct a CRSArray from a list of row element lists."""
        crs = CRSArray(num_rows, num_elements, dtype)
        for row in rows:
            crs.push_row(row)
        print("Now at ", crs.num_rows, " rows")
        return crs
