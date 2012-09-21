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

from .binary_file import BinaryFile


#-------------------------------------------------------------------------------
# CFString
#-------------------------------------------------------------------------------

class CFString(object):
    """struct __builtin_CFString { const int *isa; int flags; const char *str; long length; }"""
    SIZE = 16
    
    # See http://www.opensource.apple.com/source/CF/CF-550.42/CFString.c
    kCFHasLengthByte = 0x04
    kCFHasNullByte = 0x08
    kCFIsUnicode = 0x10
    
    def __init__(self, framework_file, offset):
        self.framework_file = framework_file
        self.objc_class, self.flags, self.pointer, self.length = self.framework_file.unpack("LLLL", offset)
        
    @property
    def string(self):
        """Read the const char* (string) portion of a CFString."""
        s = None
        
        if (self.flags & CFString.kCFHasLengthByte):
            assert ord(self.framework_file.data[self.pointer]) == self.length, "Invalid length or length byte."
            self.pointer += 1
        
        if (self.flags & CFString.kCFIsUnicode):
            bytes = self.framework_file.data[self.pointer:self.pointer + (self.length * 2)]
            last_byte = self.framework_file.data[self.pointer + (self.length * 2)]
            if self.is_little_endian:
                s = bytes.decode('utf-16le')
            else:
                s = bytes.decode('utf-16be')
        else:
            bytes = self.framework_file.data[self.pointer:self.pointer + self.length]
            last_byte = self.framework_file.data[self.pointer + self.length]
            s = bytes.decode('ascii')
        
        if (self.flags & CFString.kCFHasNullByte):
            assert last_byte == '\0', "Something went wrong reading a CFString."
            
        return s


#-------------------------------------------------------------------------------
# ArtworkSetMetadata
#-------------------------------------------------------------------------------

class ArtworkSetMetadata(object):
    SIZE = 36

    def __init__(self, framework_file, offset):
        self.framework_file = framework_file
        # sizes_offset points directly to an array of ArtworkMetadataInformation structs
        # names_offset is the address of an array of pointers to cfstrings. (yikes.)
        self.set_name_offset, _, _, self.sizes_offset, self.names_offset, self.artwork_count, _, _, _, _ = self.framework_file.unpack("LLLLLHHLLL", offset)

    def __repr__(self):
        return "ArtworkSetInformation %s [sno: %x; so: %x; no: %x; ac: %d; e: %r; o: %x]" % (self.name, self.set_name_offset, self.sizes_offset, self.names_offset, self.artwork_count, self.endian, self.offset)
    
    @property
    def name(self):
        return CFString(self.framework_file, self.set_name_offset).string

    @property
    def image_count(self):
        return self.artwork_count

    @property
    def version(self):
        return "6.0.0" # For now?

    @property
    def is_retina(self):
        return "@2x" in self.name
    
    def iter_images(self):
        size_offset = self.sizes_offset
        name_offset = self.names_offset

        # Walk through the artwork and gather information.
        for artwork_i in range(self.artwork_count):
            name_pointer = self.framework_file.read_long_at(name_offset)
            artwork_image_metadata = ArtworkImageMetadata(self.framework_file, self, size_offset, name_pointer)
            size_offset += ArtworkImageMetadata.SIZE
            name_offset += 4
            yield artwork_image_metadata

    def to_jsonable(self):
        return {
            "images": [image_metadata.to_jsonable() for image_metadata in self.iter_images()],
            "name": self.name,
            "version": self.version,
            "byte_size": self.framework_file.file_size,
        }
            

#-------------------------------------------------------------------------------
# ArtworkImageMetadata
#-------------------------------------------------------------------------------

class ArtworkImageMetadata(object):
    """
    Appears to be struct 
    { 
        unsigned int24_t offset_into_artwork_file; 
        unsigned char flags; // these are deep and mysterious.
        unsigned int width; 
        unsigned int height; 
    }
    """
    SIZE = 8

    def __init__(self, framework_file, artwork_set_metadata, size_offset, name_pointer):
        self.framework_file = framework_file
        self.artwork_set_metadata = artwork_set_metadata
        offset_with_flags, self.width, self.height = self.framework_file.unpack("LHH", size_offset)
        self.flags = (offset_with_flags & 0xFF) # Flags only
        self.image_offset = (offset_with_flags & 0xFFFFFF00) # Remove the flags
        self.name = CFString(self.framework_file, name_pointer).string

    @property
    def retina_appropriate_name(self):
        name = self.name
        if self.artwork_set_metadata.is_retina and ("@2x" not in name):
            name = name.replace(".png", "@2x.png")
        return name

    def to_jsonable(self):
        return [
            self.retina_appropriate_name,
            self.width,
            self.height,
            self.image_offset,
            self.flags,
        ]


#-------------------------------------------------------------------------------
# FrameworkFile
#-------------------------------------------------------------------------------

class FrameworkFile(BinaryFile):
    """
    Random hacknology collection for cracking open Mach-O
    framework binaries, although we partially ignore the
    Mach-O-ness of them.
    """
    def __init__(self, filename):
        super(FrameworkFile, self).__init__(filename)

    def read_artwork_set_metadata_at(self, offset):
        return ArtworkSetMetadata(self, offset)




