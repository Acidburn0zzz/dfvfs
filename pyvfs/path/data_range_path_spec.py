#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The data range path specification implementation."""

from pyvfs.path import path_spec


class DataRangePathSpec(path_spec.PathSpec):
  """Class that implements the data range path specification."""

  def __init__(self, range_offset, range_size, parent):
    """Initializes the data range path specification object.

       Note that the data range path specification must have a parent.

    Args:
      range_offset: the start offset of the data range.
      range_size: the size of the data range.
      parent: parent path specification (instance of PathSpec).
    """
    super(DataRangePathSpec, self).__init__(parent=parent)
    self.range_offset = range_offset
    self.range_size = range_size
