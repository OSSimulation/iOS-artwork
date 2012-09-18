#-------------------------------------------------------------------------------
#
# iOS .artwork file extractor
# (c)2008-2011 Dave Peck <code [at] davepeck [dot] org> All Rights Reserved
# 
# Released under the three-clause BSD license.
#
# http://github.com/davepeck/iphone-tidbits/
#
#-------------------------------------------------------------------------------

import os
import mmap
import struct
import PIL.Image # You must have the Python Imaging Library (PIL) installed

from .binary_file import BinaryFile

class ArtworkBinaryFile(BinaryFile):
    """Represents an iOS SDK .artwork file"""
    
    WIDTH_BYTE_PACKING = 8 # Determined by inspection/luck.
    
    def __init__(self, filename):
        super(ArtworkBinaryFile, self).__init__(filename)
        
    @classmethod
    def byte_size(width, height, is_greyscale):
        aligned_width = width
        remainder = aligned_width % 8
        if remainder != 0: aligned_width += (8 - remainder)

        pixel_width = 1 if is_greyscale else 4

        pixel_size = (pixel_width * ((image_height * aligned_width) + image_width))
        



    @staticmethod
    def _align(offset):
        """Perform packing alignment appropriate for image pixels in the .artwork file"""
        remainder = offset % ArtworkBinaryFile.WIDTH_BYTE_PACKING
        if remainder != 0: offset += (ArtworkBinaryFile.WIDTH_BYTE_PACKING - remainder)
        return offset        
        
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
                        r = (r*255 + a//2)//a
                        g = (g*255 + a//2)//a
                        b = (b*255 + a//2)//a
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
                        r = (r*a + 127)//255
                        g = (g*a + 127)//255
                        b = (b*a + 127)//255
                    packed = struct.pack('<BBBB', b, g, r, a)
                pixel_offset = offset + (pixel_width * ((y * aligned_width) + x))
                self.data[pixel_offset:pixel_offset + pixel_width] = packed    
        
