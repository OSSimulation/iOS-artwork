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

import struct

class Struct(object):
    pass
    

#-------------------------------------------------------------------------------
# CFString
#-------------------------------------------------------------------------------
    
class CFString(Struct):
    """struct __builtin_CFString { const int *isa; int flags; const char *str; long length; }"""
    SIZE = 16
    
    # See http://www.opensource.apple.com/source/CF/CF-550.42/CFString.c
    kCFHasLengthByte = 0x04
    kCFHasNullByte = 0x08
    kCFIsUnicode = 0x10
    
    def __init__(self, endian, data, offset):
        super(CFString, self).__init__()
        self.endian = endian
        self.data = data
        self.offset = offset
        self.objc_class, self.flags, self.pointer, self.length = struct.unpack_from(("%sLLLL" % endian), data, offset)
        self.is_little_endian = (endian == "<")
        
    @property
    def string(self):
        """Read the const char* (string) portion of a CFString."""
        s = None
        
        if (self.flags & CFString.kCFHasLengthByte):
            assert ord(self.data[self.pointer]) == self.length, "Invalid length or length byte."
            offset += 1
        
        if (self.flags & CFString.kCFIsUnicode):
            bytes = self.data[self.pointer:self.pointer+(self.length * 2)]
            last_byte = self.data[self.pointer+(self.length * 2)]
            if self.is_little_endian:
                s = bytes.decode('utf-16le')
            else:
                s = bytes.decode('utf-16be')
        else:
            bytes = self.data[self.pointer:self.pointer+self.length]
            last_byte = self.data[self.pointer+self.length]
            s = bytes.decode('ascii')
        
        if (self.flags & CFString.kCFHasNullByte):
            assert last_byte == '\0', "Something went wrong reading cfstring."
            
        return s
    
        
#-------------------------------------------------------------------------------
# NList
#-------------------------------------------------------------------------------

class NList(Struct):
    """struct nlist { int32_t n_un; uint8_t n_type; uint8_t n_sect; int16_t n_desc; uint32_t n_value; }"""
    SIZE = 12
    N_ARM_THUMB_DEF = 0x0008 # See MachOFileAbstraction.hpp
    
    def __init__(self, endian, data, offset):
        super(Struct, self).__init__()
        self.n_strx, self.n_type, self.n_sect, self.n_desc, self.n_value = struct.unpack_from(("%siBBhI" % endian), data, offset)
        
        
#-------------------------------------------------------------------------------
# ArtworkSetInformation
#-------------------------------------------------------------------------------

class ArtworkSetInformation(Struct):
    SIZE = 36

    def __init__(self, endian, data, offset):
        super(ArtworkSetInformation, self).__init__()
        # sizes_offset points directly to an array of ArtworkSizeInformation structs
        # names_offset is the address of an array of pointers to cfstrings. (yikes.)
        self.set_name_offset, unk1, unk2, self.sizes_offset, self.names_offset, self.artwork_count, unk3, unk4, unk5, unk6 = struct.unpack_from(("%sLLLLLHHLLL" % endian), data, offset)
        self.endian = endian
        self.data = data
        self.offset = offset

    def __repr__(self):
        return "ArtworkSetInformation %s [sno: %x; so: %x; no: %x; ac: %d; e: %r; o: %x]" % (self.name, self.set_name_offset, self.sizes_offset, self.names_offset, self.artwork_count, self.endian, self.offset)
    
    @property
    def name(self):
        return CFString(self.endian, self.data, self.set_name_offset).string
    
    @property
    def is_2x(self):
        return "@2x" in self.name
    
    def read_offset(self, offset):
        """Dereference an address found at `offset`"""
        return struct.unpack_from('%sL' % self.endian, self.data, offset)[0]
    
    def iter_artworks(self):
        size_offset = self.sizes_offset
        name_offset = self.names_offset

        # Walk through the artwork and gather information.
        for artwork_i in range(self.artwork_count):
            ai = ArtworkSizeInformation(self.endian, self.data, size_offset)
            name_pointer = self.read_offset(name_offset)
            name_cfstring = CFString(self.endian, self.data, name_pointer)

            size_offset += ArtworkSizeInformation.SIZE
            name_offset += 4
            
            final_name_string = name_cfstring.string
            if self.is_2x:
                final_name_split = final_name_string.split('.')
                final_name_string = "%s@2x.%s" % ('.'.join(final_name_split[0:-1]), final_name_split[-1])
            
            yield (final_name_string, ai)
            
    
#-------------------------------------------------------------------------------
# ArtworkSizeInformation
#-------------------------------------------------------------------------------

class ArtworkSizeInformation(Struct):
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
    def __init__(self, endian, data, offset):
        super(ArtworkSizeInformation, self).__init__()
        offset_with_flags, self.width, self.height = struct.unpack_from(("%sLHH" % endian), data, offset)
        self.flags = (offset_with_flags & 0xFF) # Flags only
        self.offset = (offset_with_flags & 0xFFFFFF00) # Remove the flags
        
    @property
    def is_premultiplied_alpha(self):
        return True # Appears to be true for all images
        
    @property
    def is_greyscale(self):
        # HACK. I only _think_ this is correct. It seems to be.
        return (self.flags & 0x02) != 0
    
    
        
