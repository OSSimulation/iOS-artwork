#!/usr/bin/env python

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

#
# NOTE: you almost certainly don't want or need to use this script. ;-)
#

import sys
import json
from artwork.framework_file import FrameworkFile



#-------------------------------------------------------------------------------
# __main__ :: supremely hacknological, but handy, at the moment
#-------------------------------------------------------------------------------

# Want to know what offset to toss in here?
#
# 1. Find the name of an arwork file, say Foo@2x.artwork
# 2. Use hex fiend to find the location of the string "Foo@2x\0" in the appropriate framework binary
# 3. Work backwards in the hex editor to find the CFString, and then the pointer to that CFString.
# 4. Use the offset where the pointer to the CFString is located!
#
# For example, in iOS 6.0.0, in the Assistant Mach-O binary, the offset
# you want for AssistantMic@2x.artwork is: 0x70BC0 (461760)

def main(framework_file_name, artwork_set_metadata_offset):
    framework_file = FrameworkFile(framework_file_name)
    artwork_set_metadata = framework_file.read_artwork_set_metadata_at(artwork_set_metadata_offset)
    jsonable = artwork_set_metadata.to_jsonable()
    json_string = json.dumps(jsonable, indent=4)
    print json_string    

if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
