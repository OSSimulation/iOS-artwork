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

import PIL.Image
from .binary_file import BinaryFile, WritableBinaryFile


#------------------------------------------------------------------------------
# ArtworkImage
#------------------------------------------------------------------------------

class ArtworkImage(object):
    """
    Abstract class for metadata and accessor for a single image in
    an artwork file.
    """
    def __init__(self, artwork_file, artwork_set):
        super(ArtworkImage, self).__init__()
        self.artwork_file = artwork_file
        self.artwork_set = artwork_set

    @property
    def name(self):
        raise NotImplementedError("Implement in a derived class.")

    @property
    def width(self):
        raise NotImplementedError("Implement in a derived class.")

    @property
    def height(self):
        raise NotImplementedError("Implement in a derived class.")

    @property
    def image_offset(self):
        raise NotImplementedError("Implement in a derived class.")

    @property
    def is_greyscale(self):
        raise NotImplementedError("Implement in a derived class.")

    @property
    def retina_appropriate_name(self):
        name = self.name
        if self.artwork_set.is_retina and ("@2x" not in name):
            name = name.replace(".png", "@2x.png")
        return name

    def get_pil_image(self):
        return self.artwork_file.read_pil_image_at(self.image_offset, self.width, self.height, self.is_greyscale)



#------------------------------------------------------------------------------
# ArtworkSet
#------------------------------------------------------------------------------

class ArtworkSet(object):
    """
    Abstract base class for a group of objects that repsent metadata
    for all images found in an artwork file.
    """
    def __init__(self, artwork_file):
        super(ArtworkSet, self).__init__()
        self.artwork_file = artwork_file

    @property
    def version(self):
        raise NotImplementedError("Implement in a derived class.")

    @property
    def image_count(self):
        raise NotImplementedError("Implement in a derived class.")

    def iter_images(self):
        raise NotImplementedError("Implement in a derived class.")

    @property
    def name(self):
        return self.artwork_file.basename

    @property
    def is_retina(self):
        return "@2x" in self.name


#------------------------------------------------------------------------------
# ArtworkFileCommon
#------------------------------------------------------------------------------

class ArtworkFileCommon(object):
    """
    APIs that apply to both read and write artwork files.
    """
    def byte_align(self, offset, alignment):
        """Perform packing alignment appropriate for image pixels in the .artwork file"""
        remainder = offset % alignment
        if remainder != 0:
            offset += (alignment - remainder)
        return offset

    def width_byte_align(self, width, **kwargs):
        return self.byte_align(width, self.width_byte_packing(**kwargs))

    def width_byte_packing(self, **kwargs):
        raise NotImplementedError("Implement in a derived class.")

    @property
    def artwork_set(self):
        raise NotImplementedError("Implement in a derived class.")


#------------------------------------------------------------------------------
# ArtworkFile
#------------------------------------------------------------------------------

class ArtworkFile(BinaryFile, ArtworkFileCommon):
    """Base class for reading an iOS SDK .artwork file, of any iOS era."""

    def __init__(self, filename):
        super(ArtworkFile, self).__init__(filename)
        self.greyscale_pixel_size = 1
        self.color_pixel_size = 4

    def read_greyscale_pixel_at(self, offset):
        return self.read_byte_at(offset)

    def read_color_pixel_at(self, offset):
        # Returns b, g, r, a
        return self.unpack("BBBB", offset)

    def read_pil_greyscale_pixel_at(self, offset):
        grey = self.read_greyscale_pixel_at(offset)
        return (grey, grey, grey, 255)

    def read_pil_color_pixel_at(self, offset):
        b, g, r, a = self.read_color_pixel_at(offset)
        # Handle premultiplied alpha
        if (a != 0):
            r = (r * 255 + a // 2) // a
            g = (g * 255 + a // 2) // a
            b = (b * 255 + a // 2) // a
        return (r, g, b, a)

    def read_pil_image_at(self, offset, width, height, is_greyscale):
        """Return a PIL image instance of given size, at a given offset in the .artwork file."""
        pil_image = PIL.Image.new("RGBA", (width, height))
        pil_pixels = pil_image.load()
        aligned_width = self.width_byte_align(width, is_greyscale=is_greyscale)
        pixel_width = self.greyscale_pixel_size if is_greyscale else self.color_pixel_size

        for y in range(height):
            for x in range(width):
                pixel_offset = offset + (pixel_width * ((y * aligned_width) + x))
                if is_greyscale:
                    pil_pixels[x, y] = self.read_pil_greyscale_pixel_at(pixel_offset)
                else:
                    pil_pixels[x, y] = self.read_pil_color_pixel_at(pixel_offset)

        return pil_image

    def iter_images(self):
        raise NotImplementedError("Implement in a derived class.")


#------------------------------------------------------------------------------
# WritableArtworkFile
#------------------------------------------------------------------------------

class WriteableArtworkFile(WritableBinaryFile, ArtworkFileCommon):
    """Represents a writable iOS SDK .artwork file"""

    def __init__(self, filename, template_binary):
        super(WriteableArtworkFile, self).__init__(filename, template_binary)

    def write_greyscale_pixel_at(self, offset, grey):
        self.write_byte_at(offset, grey)

    def write_color_pixel_at(self, offset, b, g, r, a):
        self.pack("BBBB", offset, b, g, r, a)

    def write_pil_greyscale_pixel_at(self, offset, r, g, b, a):
        self.write_greyscale_pixel_at(offset, grey=b)

    def write_pil_color_pixel_at(self, offset, r, g, b, a):
        # handle premultiplied alpha
        r = (r * a + 127) // 255
        g = (g * a + 127) // 255
        b = (b * a + 127) // 255
        self.write_color_pixel_at(offset, b, g, r, a)

    def write_pil_image_at(self, offset, width, height, is_greyscale, pil_image):
        """Write a PIL image instance of given size, to a given offset in the .artwork file."""
        pil_pixels = pil_image.load()
        aligned_width = self.width_byte_align(width, is_greyscale=is_greyscale)
        pixel_width = 1 if is_greyscale else 4

        for y in range(height):
            for x in range(width):
                pixel_offset = offset + (pixel_width * ((y * aligned_width) + x))

                if pil_image.mode == 'RGBA':
                    r, g, b, a = pil_pixels[x, y]
                else:
                    r, g, b = pil_pixels[x, y]
                    a = 255

                if is_greyscale:
                    self.write_pil_greyscale_pixel_at(pixel_offset, r, g, b, a)
                else:
                    self.write_pil_color_pixel_at(pixel_offset, r, g, b, a)

