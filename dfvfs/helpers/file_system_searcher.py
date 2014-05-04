#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The dfVFS Project Authors.
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
"""A searcher to find file entries within a file system."""

import re
import sre_constants

from dfvfs.lib import definitions
from dfvfs.lib import errors


class FindSpec(object):
  """Find specification object."""

  def __init__(
      self, file_entry_types=None, is_allocated=True, location=None,
      location_regex=None, case_sensitive=True):
    """Initializes the find specification object.

    Args:
      file_entry_types: Optional file entry types list or None to indicate
                        no preference. The default is None.
      is_allocated: Optional boolean value to indicate the file entry should
                    be allocated, where None represents no preference.
                    The default is True.
      location: Optional location string or list of location segments, or None
                to indicate no preference. The location should be defined
                relative to the root of the file system. The default is None.
                Note that the string will be split into segments based on the
                file system specific path segment separator.
      location_regex: Optional location regular expression string or list of
                      location regular expression segments, or None to indicate
                      no preference. The location regular expression should be
                      defined relative to the root of the file system. The
                      default is None. Note that the string will be split into
                      segments based on the file system specific path segment
                      separator.
      case_sensitive: Optional boolean value to indicate string matches should
                      be case sensitive. The default is true.

    Raises:
      TypeError: if the location or location_regex type is not supported.
      ValueError: if both location and location_regex are set.
    """
    if location is not None and location_regex is not None:
      raise ValueError(
          u'The location and location_regex arguments cannot be used at same '
          u'time.')

    super(FindSpec, self).__init__()
    self._file_entry_types = file_entry_types
    self._is_allocated = is_allocated
    self._is_case_sensitive = case_sensitive
    self._is_regex = None
    self._location = None
    self._location_regex = None
    self._location_segments = None
    self._number_of_location_segments = 0

    # TODO: add support for globbing?
    if location is not None:
      if isinstance(location, basestring):
        self._location = location
      elif isinstance(location, list):
        self._location_segments = location
      else:
        raise TypeError(u'Unsupported location type: {0:s}.'.format(
            type(location)))

      self._is_regex = False

    elif location_regex is not None:
      if isinstance(location_regex, basestring):
        self._location_regex = location_regex
      elif isinstance(location_regex, list):
        self._location_segments = location_regex
      else:
        raise TypeError(u'Unsupported location_regex type: {0:s}.'.format(
            type(location_regex)))

      self._is_regex = True

    # TODO: add support for name
    # TODO: add support for owner (user, group)
    # TODO: add support for permissions (mode)
    # TODO: add support for size
    # TODO: add support for time values
    # TODO: add support for expression e.g.
    # attribute['$FILE_NAME'].creation_type == 'x'

  def _CheckFileEntryType(self, file_entry):
    """Checks the file entry type find specifications.

    Args:
      file_entry: the file entry (instance of vfs.FileEntry).

    Returns:
      True if the file entry matches the find specification false otherwise.
    """
    return (self._CheckIsDevice(file_entry) or
            self._CheckIsDirectory(file_entry) or
            self._CheckIsFile(file_entry) or
            self._CheckIsLink(file_entry) or
            self._CheckIsPipe(file_entry) or
            self._CheckIsSocket(file_entry))

  def _CheckIsAllocated(self, file_entry):
    """Checks the is_allocated find specification.

    Args:
      file_entry: the file entry (instance of vfs.FileEntry).

    Returns:
      True if the file entry matches the find specification false otherwise.
    """
    return (self._is_allocated is not None and
            self._is_allocated == file_entry.IsAllocated())

  def _CheckIsDevice(self, file_entry):
    """Checks the is_device find specification.

    Args:
      file_entry: the file entry (instance of vfs.FileEntry).

    Returns:
      True if the file entry matches the find specification false otherwise.
    """
    if (self._file_entry_types is not None and
        definitions.FILE_ENTRY_TYPE_DEVICE not in self._file_entry_types):
      return False
    return file_entry.IsDevice()

  def _CheckIsDirectory(self, file_entry):
    """Checks the is_directory find specification.

    Args:
      file_entry: the file entry (instance of vfs.FileEntry).

    Returns:
      True if the file entry matches the find specification false otherwise.
    """
    if (self._file_entry_types is not None and
        definitions.FILE_ENTRY_TYPE_DIRECTORY not in self._file_entry_types):
      return False
    return file_entry.IsDirectory()

  def _CheckIsFile(self, file_entry):
    """Checks the is_file find specification.

    Args:
      file_entry: the file entry (instance of vfs.FileEntry).

    Returns:
      True if the file entry matches the find specification false otherwise.
    """
    if (self._file_entry_types is not None and
        definitions.FILE_ENTRY_TYPE_FILE not in self._file_entry_types):
      return False
    return file_entry.IsFile()

  def _CheckIsLink(self, file_entry):
    """Checks the is_link find specification.

    Args:
      file_entry: the file entry (instance of vfs.FileEntry).

    Returns:
      True if the file entry matches the find specification false otherwise.
    """
    if (self._file_entry_types is not None and
        definitions.FILE_ENTRY_TYPE_LINK not in self._file_entry_types):
      return False
    return file_entry.IsLink()

  def _CheckIsPipe(self, file_entry):
    """Checks the is_pipe find specification.

    Args:
      file_entry: the file entry (instance of vfs.FileEntry).

    Returns:
      True if the file entry matches the find specification false otherwise.
    """
    if (self._file_entry_types is not None and
        definitions.FILE_ENTRY_TYPE_PIPE not in self._file_entry_types):
      return False
    return file_entry.IsPipe()

  def _CheckIsSocket(self, file_entry):
    """Checks the is_socket find specification.

    Args:
      file_entry: the file entry (instance of vfs.FileEntry).

    Returns:
      True if the file entry matches the find specification false otherwise.
    """
    if (self._file_entry_types is not None and
        definitions.FILE_ENTRY_TYPE_SOCKET not in self._file_entry_types):
      return False
    return file_entry.IsSocket()

  def AtMaximumDepth(self, search_depth):
    """Determines if the find specification is at maximum depth.

    Args:
      search_depth: the search depth.

    Returns:
      True if at maximum depth, false otherwise.
    """
    if self._location_segments is not None:
      if search_depth == self._number_of_location_segments:
        return True

    return False

  def Initialize(self, file_system):
    """Initializes find specification for matching.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
    """
    if self._location is not None:
      self._location_segments = file_system.SplitPath(self._location)

    elif self._location_regex is not None:
      self._location_segments = file_system.SplitPath(self._location_regex)

    if self._location_segments is not None:
      self._number_of_location_segments = len(self._location_segments)

  def Matches(self, file_entry, search_depth):
    """Determines if the file entry matches the find specification.

    Args:
      file_entry: the file entry (instance of vfs.FileEntry).
      search_depth: the search depth.

    Returns:
      True if the file entry matches the find specification, false otherwise.
    """
    if self._location_segments is not None:
      if search_depth < 0 or search_depth > self._number_of_location_segments:
        return False

      # Note that the root has no entry in the location segments and
      # no name to match.
      if search_depth == 0:
        segment_name = u''
      else:
        segment_name = self._location_segments[search_depth - 1]

        if self._is_regex:
          if isinstance(segment_name, basestring):
            # Allow '\n' to be matched by '.' and make '\w', '\W', '\b', '\B',
            # '\d', '\D', '\s' and '\S' Unicode safe.
            flags = re.DOTALL | re.UNICODE
            if not self._is_case_sensitive:
              flags |= re.IGNORECASE

            try:
              segment_name = r'^{0:s}$'.format(segment_name)
              segment_name = re.compile(segment_name, flags=flags)
            except sre_constants.error:
              return False

            self._location_segments[search_depth - 1] = segment_name

        elif not self._is_case_sensitive:
          segment_name = segment_name.lower()
          self._location_segments[search_depth - 1] = segment_name

      if search_depth > 0 and self._is_regex:
        if not segment_name.match(file_entry.name):
          return False

      elif search_depth == 0 or self._is_case_sensitive:
        if segment_name != file_entry.name:
          return False

      elif segment_name != file_entry.name.lower():
        return False

      if search_depth != self._number_of_location_segments:
        return False

    if not self._CheckFileEntryType(file_entry):
      return False

    if not self._CheckIsAllocated(file_entry):
      return False

    return True


class FileSystemSearcher(object):
  """Searcher object to find file entries within a file system."""

  # Type indicators that do not have a parent.
  _PARENTLESS_TYPE_INDICATORS = frozenset([
      definitions.TYPE_INDICATOR_FAKE,
      definitions.TYPE_INDICATOR_OS])

  def __init__(self, file_system, mount_point):
    """Initializes the file system searcher.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
      mount_point: the mount point path specification (instance of
                   path.PathSpec).

    Raises:
      PathSpecError: if the mount point path specification is incorrect.
      ValueError: when file system or mount point is not set.
    """
    if not file_system or not mount_point:
      raise ValueError(u'Missing file system or mount point value.')

    if file_system.type_indicator in self._PARENTLESS_TYPE_INDICATORS:
      if not hasattr(mount_point, 'location'):
        raise errors.PathSpecError(
            u'Mount point path specification missing location.')

    super(FileSystemSearcher, self).__init__()

    self._file_system = file_system
    self._mount_point = mount_point

  def _FindInFileEntry(self, file_entry, find_specs, search_depth):
    """Searches for matching file entries within the file entry.

    Args:
      file_entry: the file entry (instance of vfs.FileEntry).
      find_specs: a list of find specifications (instances of FindSpec).
      search_depth: the search depth.

    Yields:
      The path specification of the matching file entries (instances of
      path.PathSpec).
    """
    sub_find_specs = []
    for find_spec in find_specs:
      if find_spec.Matches(file_entry, search_depth):
        yield file_entry.path_spec
      if not find_spec.AtMaximumDepth(search_depth):
        sub_find_specs.append(find_spec)

    if not sub_find_specs: 
      return

    search_depth += 1
    try:
      for sub_file_entry in file_entry.sub_file_entries:
        for matching_path_spec in self._FindInFileEntry(
            sub_file_entry, sub_find_specs, search_depth):
          yield matching_path_spec
    except errors.AccessError:
      pass

  def Find(self, find_specs=None):
    """Searches for matching file entries within the file system.

    Args:
      find_specs: a list of find specifications (instances of FindSpec).
                  The default is None, which will return all allocated
                  file entries.

    Yields:
      The path specification of the matching file entries (instances of
      path.PathSpec).
    """
    if not find_specs:
      find_specs.append(FindSpec())

    for find_spec in find_specs:
      find_spec.Initialize(self._file_system)

    if self._file_system.type_indicator in self._PARENTLESS_TYPE_INDICATORS:
      file_entry = self._file_system.GetFileEntryByPathSpec(self._mount_point)
    else:
      file_entry = self._file_system.GetRootFileEntry()

    for matching_path_spec in self._FindInFileEntry(file_entry, find_specs, 0):
      yield matching_path_spec

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    return self._file_system.GetFileEntryByPathSpec(path_spec)

  def SplitPath(self, path):
    """Splits the path into path segments.

    Args:
      path: a string containing the path.

    Returns:
      A list of path segements without the root path segment, which is an
      empty string.
    """
    return self._file_system.SplitPath(path)
