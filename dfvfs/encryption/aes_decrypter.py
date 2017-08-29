# -*- coding: utf-8 -*-
"""The AES decrypter implementation."""

from __future__ import unicode_literals

from cryptography.hazmat import backends
from cryptography.hazmat.primitives import ciphers
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import modes

from dfvfs.encryption import decrypter
from dfvfs.encryption import manager
from dfvfs.lib import definitions


class AESDecrypter(decrypter.Decrypter):
  """AES decrypter using pycrypto."""

  ENCRYPTION_METHOD = definitions.ENCRYPTION_METHOD_AES

  _ENCRYPTION_MODES = frozenset([
      definitions.ENCRYPTION_MODE_CBC,
      definitions.ENCRYPTION_MODE_CFB,
      definitions.ENCRYPTION_MODE_ECB,
      definitions.ENCRYPTION_MODE_OFB])

  def __init__(
      self, cipher_mode=None, initialization_vector=None, key=None, **kwargs):
    """Initializes a decrypter.

    Args:
      cipher_mode (Optional[str]): cipher mode.
      initialization_vector (Optional[bytes]): initialization vector.
      key (Optional[bytes]): key.
      kwargs (dict): keyword arguments depending on the decrypter.

    Raises:
      ValueError: when key is not set, block cipher mode is not supported,
          or initialization_vector is required and not set.
    """
    if not key:
      raise ValueError('Missing key.')

    if cipher_mode not in self._ENCRYPTION_MODES:
      raise ValueError('Unsupported cipher mode: {0!s}'.format(cipher_mode))

    if cipher_mode != definitions.ENCRYPTION_MODE_ECB and not initialization_vector:
      raise ValueError('Missing initialization vector.')

    super(AESDecrypter, self).__init__()
    if cipher_mode == definitions.ENCRYPTION_MODE_CBC:
      mode = modes.CBC(initialization_vector)
    elif cipher_mode == definitions.ENCRYPTION_MODE_CFB:
      mode = modes.CFB(initialization_vector)
    elif cipher_mode == definitions.ENCRYPTION_MODE_ECB:
      mode = modes.ECB()
    elif cipher_mode == definitions.ENCRYPTION_MODE_OFB:
      mode = modes.OFB(initialization_vector)

    self._algorithm = algorithms.AES(key)
    backend = backends.default_backend()
    cipher = ciphers.Cipher(self._algorithm, mode, backend=backend)
    self._cipher_context = cipher.decryptor()

  def Decrypt(self, encrypted_data):
    """Decrypts the encrypted data.

    Args:
      encrypted_data (bytes): encrypted data.

    Returns:
      tuple[bytes, bytes]: decrypted data and remaining encrypted data.
    """
    index_split = -(len(encrypted_data) % self._algorithm.block_size)
    if index_split:
      remaining_encrypted_data = encrypted_data[index_split:]
      encrypted_data = encrypted_data[:index_split]
    else:
      remaining_encrypted_data = b''

    decrypted_data = self._cipher_context.update(encrypted_data)

    return decrypted_data, remaining_encrypted_data


manager.EncryptionManager.RegisterDecrypter(AESDecrypter)
