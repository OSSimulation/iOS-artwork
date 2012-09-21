#-------------------------------------------------------------------------------
#
# iOS .artwork file extractor
# (c)2008-2012 Dave Peck <davepeck [at] davepeck [dot] org> All Rights Reserved
# 
# Released under the three-clause BSD license.
#
# http://github.com/davepeck/iOS-artwork/
#
#-------------------------------------------------------------------------------

import os
import os.path
import struct
import mmap


#------------------------------------------------------------------------------
# BinaryFile
#------------------------------------------------------------------------------

class BinaryFile(object):
    """
    A read-only binary file on disk, with some basic tools to read from it.
    """
    BYTE = 1
    SHORT = 2
    LONG = 4

    def __init__(self, filename, endian="<"):
        super(BinaryFile, self).__init__()
        self.filename = filename
        self._file = None
        self._data = None
        self._data_length = -1
        self._endian = endian
        
    def __del__(self):
        if self._data is not None:
            self._data.close()
            self._data = None
        if self._file is not None:
            self._file.close()
            self._file = None

    @property
    def basename(self):
        return os.path.basename(self.filename)
            
    @property
    def file_size(self):
        return os.path.getsize(self.filename)
            
    @property
    def data(self):
        if self._data is None:
            self._file = open(self.filename, "rb")
            self._data = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)
        return self._data
        
    @property
    def data_length(self):
        if self._data_length == -1:
            self._data_length = len(self.data)
        return self._data_length

    def unpack(self, structure, offset):
        return struct.unpack_from("%s%s" % (self._endian, structure), self.data, offset)

    def read_long_at(self, offset):
        return self.unpack("L", offset)[0]

    def read_short_at(self, offset):
        return self.unpack("H", offset)[0]

    def read_byte_at(self, offset):
        return self.unpack("B", offset)[0]

    def read_null_terminated_utf8_string_at(self, offset):
        start = offset
        while ord(self.data[offset]) != 0:
            offset += 1
        bytes = self.data[start:offset]
        return bytes.decode("utf-8")


#------------------------------------------------------------------------------
# WritableBinaryFile
#------------------------------------------------------------------------------

class WritableBinaryFile(BinaryFile):
    """
    A writable binary file on disk, backed by a template read-only binary.
    """
    def __init__(self, filename, template_binary, endian="<"):
        super(WritableBinaryFile, self).__init__(filename, endian)
        self.template_binary = template_binary
        self._data_length = template_binary.data_length

    @property
    def data(self):
        if self._data is None:
            # Copy over the template binary's contents
            self._file = open(self.filename, "wb")
            self._file.write(self.template_binary.data)
            self._file.close()

            self._file = open(self.filename, "r+b")
            self._data = mmap.mmap(self._file.fileno(), self.data_length, access=mmap.ACCESS_WRITE)
        return self._data
    
    @property
    def data_length(self):
        return self._data_length
        
    def open(self):
        return self.data  # HACK -- obviously a bogus OM.
        
    def close(self):
        self._data.flush()
        self._data.close()
        self._file.close()
        self._data = None
        self._file = None
        
    def delete(self):
        self.close()
        os.remove(self.filename)

    def pack(self, structure, offset, *values):
        struct.pack_into("%s%s" % (self._endian, structure), self.data, offset, *values)

    def write_long_at(self, offset, l):
        self.pack("L", offset, l)

    def write_short_at(self, offset, h):
        self.pack("H", offset, h)

    def write_byte_at(self, offset, b):
        self.pack("B", offset, b)

    def write_null_terminated_utf8_string_at(self, offset, s):
        bytes = s.encode("utf-8")
        for byte in bytes:
            self.data[offset] = byte
            offset += 1
        self.data[offset] = chr(0)



