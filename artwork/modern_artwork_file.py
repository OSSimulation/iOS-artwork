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

from .artwork_file import ArtworkImage, ArtworkSet, ArtworkFile, WriteableArtworkFile

#
# Modern *.artwork files are found in iOS6 and (hopefully) above.
# Just about all of the iOS6 SDK artwork files are "modern" -- there appear
# to be a handful of stragglers.
#
# Unlike previous generations of iOS, these files are self-contained:
# they contain both the images (in raw RGBA and/or greyscale form)
# and they contain the metadata (names, sizes, byte offsets) for the
# images. This means that ModernArtwork* classes have code to crack
# this metadata directly from the artwork file in question -- no need
# to crack a mach-o binary for metadata anymore! (Thank goodness.)
#
# iOS6 artwork files start with a header, and end with image contents.
# The header is packed as follows:
#
# image_count: LONG
# offset_to_information_array: LONG
# image_name_offsets_array: image_count array of LONG
# information_array: image_count array of 12-byte values, each of which is:
#   flags: LONG -- stuff like the color space, and mysterious other things
#   width: SHORT
#   height: SHORT
#   offset: LONG
#


#------------------------------------------------------------------------------
# ModernArtworkImage: for iOS6 and (hopefully) beyond
#------------------------------------------------------------------------------

class ModernArtworkImage(ArtworkImage):
    SIZE = 12

    def __init__(self, artwork_file, artwork_set, name, info_offset):
        super(ModernArtworkImage, self).__init__(artwork_file, artwork_set)
        self._name = name
        self._flags, self._width, self._height, self._image_offset = self.artwork_file.unpack("LHHL", info_offset)

    @property
    def name(self):
        return self._name

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def image_offset(self):
        return self._image_offset

    @property
    def is_greyscale(self):
        return (self._flags & 0x02) != 0        


#------------------------------------------------------------------------------
# ModernArtworkSet
#------------------------------------------------------------------------------

class ModernArtworkSet(ArtworkSet):
    _NAME_OFFSET_ARRAY_OFFSET = 8

    def __init__(self, artwork_file):
        super(ModernArtworkSet, self).__init__(artwork_file)

    @property
    def version(self):
        return "iOS6+"

    @property
    def image_count(self):
        return self.artwork_file.read_long_at(0)

    @property
    def _image_info_array_offset(self):
        return self.artwork_file.read_long_at(4)

    def iter_images(self):
        info_offset = self._image_info_array_offset
        name_offset_offset = ModernArtworkSet._NAME_OFFSET_ARRAY_OFFSET
        for i in range(self.image_count):
            name_offset = self.artwork_file.read_long_at(name_offset_offset)
            name = self.artwork_file.read_null_terminated_utf8_string_at(name_offset)
            yield ModernArtworkImage(self.artwork_file, self, name, info_offset)
            name_offset_offset += ModernArtworkFile.LONG
            info_offset += ModernArtworkImage.SIZE


#------------------------------------------------------------------------------
# ModernArtworkFile
#------------------------------------------------------------------------------

class ModernArtworkFile(ArtworkFile):
    def __init__(self, filename):
        super(ModernArtworkFile, self).__init__(filename)

    @property
    def width_byte_packing(self):
        return 1

    @property
    def artwork_set(self):
        return ModernArtworkSet(self)

    @property
    def is_legacy(self):
        return False

    @property
    def is_modern(self):
        return True

    @property
    def is_modern_supported(self):
        artwork_set = self.artwork_set
        return (artwork_set.image_count > 0) and (artwork_set.image_count <= 4096)


#------------------------------------------------------------------------------
# ModernWriteableArtworkFile
#------------------------------------------------------------------------------

class WriteableModernArtworkFile(WriteableArtworkFile):
    def __init__(self, filename, template_binary):
        super(WriteableModernArtworkFile, self).__init__(filename, template_binary)

    @property
    def width_byte_packing(self):
        return 1

    @property
    def artwork_set(self):
        return self.template_binary.artwork_set()

    
