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

# iOS-artwork.py
#
# This script makes it easy to extract images from the .artwork files found
# in the iOS SDK. To use it, you must have python and the Python Imaging Libraries
# (PIL) installed.
#
# Run it as:
#
#   ./iOS-artwork.py export -a artwork_file.artwork -d export_directory
#
#
# Please see the README file for more details.

import os
import sys
import PIL
import PIL.Image
from optparse import OptionParser

# import PIL.Image

from artwork.legacy_artwork_file import LegacyArtworkFile, WriteableLegacyArtworkFile
from artwork.modern_artwork_file import ModernArtworkFile, WriteableModernArtworkFile

def usage(parser):
    parser.print_help()
    sys.exit(-1)

def bail(message):
    print("\n%s\n" % message)
    sys.exit(-1)

def file_extension(file_name):
    return os.path.splitext(file_name)[1][1:]
    
def action_export(artwork_file_name, directory):
    artwork_file = LegacyArtworkFile(artwork_file_name)
    if not artwork_file.is_legacy_supported:
        artwork_file = ModernArtworkFile(artwork_file_name)
        if not artwork_file.is_modern_supported:
            bail("FAIL. This tool does not currently support %s" % artwork_file_name)

    artwork_set = artwork_file.artwork_set
    print("\nExporting %d images from %s (version %s)..." % (artwork_set.image_count, artwork_set.name, artwork_set.version))
    
    for artwork_image in artwork_set.iter_images():
        pil_image = artwork_image.get_pil_image()
        export_file_name = os.path.join(directory, artwork_image.retina_appropriate_name)
        pil_image.save(export_file_name, file_extension(export_file_name))
        print("\texported %s" % export_file_name)
        
    print("\nDONE EXPORTING!")
    
def main(argv):
    #
    # Set up command-line options parser
    #
    parser = OptionParser(usage = """%prog -a artwork_file.artwork -d export_directory

    -a artwork_file.artwork 
    -d export_directory
    
    Exports the contents of artwork_file.artwork as a set
    of images in the export_directory

    """)
    parser.add_option("-a", "--artwork", dest="artwork_file_name", help="Specify the input artwork file name. (Read-only.)", default = None)
    parser.add_option("-d", "--directory", dest="directory", help="Specify the directory to export images to/import images from.", default = None)

    #
    # Parse
    #
    (options, arguments) = parser.parse_args()
    
    #
    # Validate
    #
    if (options.artwork_file_name is None) or (options.directory is None):
        usage(parser)
        
    abs_artwork_file_name = os.path.abspath(options.artwork_file_name)
    
    if not os.path.exists(abs_artwork_file_name):
        bail("No artwork file named %s was found." % options.artwork_file_name)
        
    abs_directory = os.path.abspath(options.directory)
    
    if not os.path.exists(abs_directory):
        bail("No directory named %s was found." % options.directory)

    #
    # Execute
    #

    action_export(abs_artwork_file_name, abs_directory)

            
if __name__ == "__main__":
    main(sys.argv)
    

    
