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
import mmap
import struct
import PIL.Image # You must have the Python Imaging Library (PIL) installed

from .binary_file import BinaryFile

class ModernArtworkStruct(object):
    LONG = 4
    SHORT = 2
    BYTE = 1

    def __init__(self, data, endian="<"):
        super(ModernArtworkStruct, self).__init__()
        self.endian = endian
        self.data = data

    def unpack(self, structure, offset):
        return struct.unpack_from("%s%s" % (self.endian, structure), self.data, offset)

    def read_long_at(self, offset):
        return self.unpack("L", offset)[0]

    def read_short_at(self, offset):
        return self.unpack("H", offset)[0]

    def read_null_terminated_utf8_string_at(self, offset):
        start = offset
        while ord(self.data[offset]) != 0:
            offset += 1
        bytes = self.data[start:offset]
        return bytes.decode("utf-8")
    
    
class ModernArtworkSetInfo(ModernArtworkStruct):
    """
    Represents the full header for an iOS6+ .artwork file. 
    (Prior to iOS6, this information was in the framework binaries, not the
    artwork files themselves -- that was *far* harder to crack open.)

    The header in iOS6 artwork files is as follows:

    count: LONG
    offset to artwork info array: LONG
    array of offsets to artwork names: LONG * count
    array of arwork image descriptions: 12-bytes * count
    """
    def __init__(self, data, name, endian="<"):
        super(ModernArtworkSetInfo, self).__init__(data, endian)
        self.name = name

    @property
    def version(self):
        return "iOS6 or above"

    @property
    def image_infos_offset(self):
        return self.read_long_at(4)

    @property
    def name_offsets_offset(self):
        return 8

    @property
    def image_count(self):
        """Return the number of artworks in this file."""
        return self.read_long_at(0)

    def iter_images(self):
        info_offset = self.image_infos_offset
        name_offset_offset = self.name_offsets_offset
        for i in range(self.image_count):
            name_offset = self.read_long_at(name_offset_offset)
            name = self.read_null_terminated_utf8_string_at(name_offset)
            yield ModernArtworkImageInfo(self.data, info_offset, name, self.endian)
            name_offset_offset += ModernArtworkStruct.LONG
            info_offset += ModernArtworkImageInfo.SIZE


class ModernArtworkImageInfo(ModernArtworkStruct):
    """
    Represents a single image description, a part of the overall
    iOS6 .artwork header.
        flags: LONG
        width: SHORT
        height: SHORT
        image offset: LONG
    """
    SIZE = 12

    def __init__(self, data, offset, name, endian="<"):
        super(ModernArtworkImageInfo, self).__init__(data, endian)
        self.flags, self.width, self.height, self.offset = self.unpack("LHHL", offset)
        self.name = name

    @property
    def is_premultiplied_alpha(self):
        return True # Appears to be true for all images

    @property
    def is_greyscale(self):
        # HACK. I only _think_ this is correct. It seems to be.
        return (self.flags & 0x02) != 0


class ArtworkBinaryFile(BinaryFile):
    """Represents an iOS SDK .artwork file"""
    
    WIDTH_BYTE_PACKING = 1 # Determined by inspection/luck.
    
    def __init__(self, filename):
        super(ArtworkBinaryFile, self).__init__(filename)
        
    @staticmethod
    def _align(offset):
        """Perform packing alignment appropriate for image pixels in the .artwork file"""
        remainder = offset % ArtworkBinaryFile.WIDTH_BYTE_PACKING
        if remainder != 0: 
            offset += (ArtworkBinaryFile.WIDTH_BYTE_PACKING - remainder)
        return offset   

    def get_modern_artwork_set_info(self):
        return ModernArtworkSetInfo(self.data, self.basename)
        
    def get_pil_image(self, info):
        """Return a PIL image instance of given size, at a given offset in the .artwork file."""
        width = info.width
        height = info.height
        offset = info.offset
        
        pil_image = PIL.Image.new("RGBA", (width, height))
        pil_pixels = pil_image.load()

        aligned_width = ArtworkBinaryFile._align(width)
        pixel_width = 1 if info.is_greyscale else 4

        for y in range(height):
            for x in range(width):
                pixel_offset = offset + (pixel_width * ((y * aligned_width) + x))
                if info.is_greyscale:
                    gray = struct.unpack_from('<B', self.data, pixel_offset)[0]
                    a = 255
                    pil_pixels[x, y] = (gray, gray, gray, a)
                else:
                    b, g, r, a = struct.unpack_from('<BBBB', self.data, pixel_offset)
                    if (info.is_premultiplied_alpha) and (a != 0):
                        r = (r * 255 + a // 2) // a
                        g = (g * 255 + a // 2) // a
                        b = (b * 255 + a // 2) // a
                    pil_pixels[x, y] = (r, g, b, a)
                
        return pil_image       
        

class WritableArtworkBinaryFile(ArtworkBinaryFile):
    """Represents a writable iOS SDK .artwork file"""
    
    def __init__(self, filename, template_binary):
        super(WritableArtworkBinaryFile, self).__init__(filename)
        self._data_length = template_binary.data_length
        self.template_binary = template_binary
    
    @property
    def data(self):
        if self._data is None:
            # Zero out the file...
            self._file = open(self.filename, "wb")
            self._file.write(self.template_binary.data) # TODO: I don't know why I can't just zero out. Is there something else in these artwork files?
            self._file.close()

            self._file = open(self.filename, "r+b")
            self._data = mmap.mmap(self._file.fileno(), self.data_length, access=mmap.ACCESS_WRITE)
        return self._data
    
    @property
    def data_length(self):
        return self._data_length
        
    def open(self):
        # HACK. Clearly not the right object model.
        ignored = self.data
        ignored = ignored # Linters
        
    def close(self):
        self._data.flush()
        self._data.close()
        self._file.close()
        self._data = None
        self._file = None
        
    def delete(self):
        self.close()
        os.remove(self.filename)
        
    def write_pil_image(self, info, pil_image):
        """Write a PIL image instance of given size, to a given offset in the .artwork file."""
        width = info.width
        height = info.height
        offset = info.offset
        
        pil_pixels = pil_image.load()
        
        aligned_width = ArtworkBinaryFile._align(width)
        pixel_width = 1 if info.is_greyscale else 4
        
        for y in range(height):
            for x in range(width):
                if pil_image.mode == 'RGBA':
                    r, g, b, a = pil_pixels[x, y]
                else:
                    r, g, b = pil_pixels[x, y]
                    a = 255
                if info.is_greyscale:
                    packed = struct.pack('<B', b)
                else:
                    if info.is_premultiplied_alpha:
                        r = (r * a + 127) // 255
                        g = (g * a + 127) // 255
                        b = (b * a + 127) // 255
                    packed = struct.pack('<BBBB', b, g, r, a)
                pixel_offset = offset + (pixel_width * ((y * aligned_width) + x))
                self.data[pixel_offset:pixel_offset + pixel_width] = packed    
        
