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

from .macho_file import MachOBinaryFile
from .structs import ArtworkSetInformation

class UIKitBinaryFile(MachOBinaryFile):
    """Represents the UIKit framework binary, with special tools to look for artwork."""

    def __init__(self, filename):
        super(MachOBinaryFile, self).__init__(filename)
        
    @property
    def images_offset(self):
        return self.find_symbol("___images")
    
    @property
    def mapped_images_offset(self):
        return self.find_symbol("___mappedImages")
        
    @property
    def shared_image_sets_offset(self):
        return self.find_symbol("___sharedImageSets")

    @property
    def shared_iphone_image_sets_offset(self):
        return self.find_symbol("___sharedImageSetsPhone")
        
    @property
    def shared_ipad_image_sets_offset(self):
        return self.find_symbol("___sharedImageSetsPad")
        
    @property
    def emoji_mapped_image_set_offset(self):
        return self.find_symbol("_EmojiMappedImageSet")
        
    @property
    def emoji_mapped_image_set_2x_offset(self):
        return self.find_symbol("_EmojiMappedImageSet2x")
        
    @property
    def emoji_mapped_image_set_ipad_offset(self):
        return self.find_symbol("_EmojiMappedImageSet_iPad")
        
    def shared_image_sets_count(self, version_string):
        # TODO I figure this has got to be available in some symbol
        # somewhere in the UIKit binary, but... I can't find it.
        # (The obvious choice, ___sharedImageSetsCount, is actually a
        # BSS section symbol, so apparently not what we're looking for.)
        version_major = int(version_string.split('.')[0])
        version_minor = int(version_string.split('.')[1])
        if (version_major >= 5):
            if (version_minor == 0):
                return 3
            return 4
        return 2
        # return 3 if version_major >= 5 else 2

    def read_artwork_set_information(self, offset):
        return ArtworkSetInformation(self.default_endian, self.data, offset)

    def iter_shared_image_sets(self, version_string):
        offset = self.shared_image_sets_offset
        for artwork_set_i in range(self.shared_image_sets_count(version_string)):
            yield self.read_artwork_set_information(offset)
            offset += ArtworkSetInformation.SIZE

    def iter_shared_iphone_image_sets(self, version_string):
        offset = self.shared_iphone_image_sets_offset
        for artwork_set_i in range(self.shared_image_sets_count(version_string)):
            yield self.read_artwork_set_information(offset)
            offset += ArtworkSetInformation.SIZE

    def iter_shared_ipad_image_sets(self, version_string):
        offset = self.shared_ipad_image_sets_offset
        for artwork_set_i in range(self.shared_image_sets_count(version_string)):
            yield self.read_artwork_set_information(offset)
            offset += ArtworkSetInformation.SIZE
            
    @property 
    def emoji_mapped_image_set(self):
        return self.read_artwork_set_information(self.emoji_mapped_image_set_offset)
        
    @property
    def emoji_mapped_image_set_2x(self):
        return self.read_artwork_set_information(self.emoji_mapped_image_set_2x_offset)
        
    @property
    def emoji_mapped_image_set_ipad(self):
        return self.read_artwork_set_information(self.emoji_mapped_image_set_ipad_offset)


