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
import json
from .artwork_file import ArtworkImage, ArtworkSet, ArtworkFile, WriteableArtworkFile

#
# Legacy *.artwork files are found in iOS5 and earlier.
#
# These artwork files contain images in raw RGBA and/or greyscale form,
# but the problem is that the metadata needed to extract those images
# (namely, their names, sizes, colorspaces, and byte offsets in the file) 
# are *not* found in the artwork file. Instead, the metadata are found
# in a motley assortment of Mach-O binaries. For example, you can find
# the metadata for iOS5's Shared~iphone.artwork in the UIKit binary.
#
# If you look through the history of this repo, you'll discover a script
# (now deleted) called generate-from-macho-binary.py that looks for
# (unexported) symbols that point to the metadata table. That script
# outputs the files now housed in the legacy_metadata/ directory.
# 
# In order to crack a legacy artwork binary file, it must be married
# with a corresponding json file. If the json file is missing, the file
# is not supported, although you could try and support it by going 
# back in time and running generate-from-macho-binary.py yourself.
#


#------------------------------------------------------------------------------
# LegacyArtworkImage: for iOS6 and (hopefully) beyond
#------------------------------------------------------------------------------

class LegacyArtworkImage(ArtworkImage):
    def __init__(self, artwork_file, artwork_set, jsonable):
        super(LegacyArtworkImage, self).__init__(artwork_file, artwork_set)
        try:
            self._name, self._width, self._height, self._image_offset, self._flags = jsonable
        except Exception:
            # iOS3 json files don't even have the flags info
            self._name, self._width, self._height, self._image_offset = jsonable
            self._flags = 0

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
# LegacyArtworkSet
#------------------------------------------------------------------------------

class LegacyArtworkSet(ArtworkSet):
    def __init__(self, artwork_file, jsonable):
        super(LegacyArtworkSet, self).__init__(artwork_file)
        self._jsonable = jsonable

    @property
    def version(self):
        return self._jsonable["version"]

    @property
    def image_count(self):
        return len(self._jsonable["images"])

    def iter_images(self):
        for image_jsonable in self._jsonable["images"]:
            yield LegacyArtworkImage(self.artwork_file, self, image_jsonable)


#------------------------------------------------------------------------------
# LegacyArtworkFile
#------------------------------------------------------------------------------

class LegacyArtworkFile(ArtworkFile):
    def __init__(self, filename):
        super(LegacyArtworkFile, self).__init__(filename)

    @property
    def width_byte_packing(self):
        return 8

    @property
    def artwork_set(self):
        return LegacyArtworkSet(self, self.legacy_jsonable)

    @property
    def _script_directory(self):
        return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    @property
    def _legacy_metadata_directory(self):
        return os.path.join(self._script_directory, "legacy_metadata")

    @property
    def _legacy_metadata_json_file_name(self):
        return os.path.join(self._legacy_metadata_directory, "%s-%d.json" % (self.basename, self.file_size))

    @property
    def is_legacy_supported(self):
        legacy_metadata_json_file_name = self._legacy_metadata_json_file_name
        return os.path.exists(legacy_metadata_json_file_name)

    @property
    def legacy_jsonable(self):
        with open(self._legacy_metadata_json_file_name) as f:
            jsonable = json.loads(f.read())
        return jsonable


#------------------------------------------------------------------------------
# LegacyWriteableArtworkFile
#------------------------------------------------------------------------------

class LegacyWriteableArtworkFile(WriteableArtworkFile):
    # XXX TODO
    def __init__(self, filename, template_binary):
        super(LegacyWriteableArtworkFile, self).__init__(filename, template_binary)

    @property
    def width_byte_packing(self):
        return 8

    @property
    def artwork_set(self):
        return self.template_binary.artwork_set()

    
