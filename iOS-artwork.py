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
# You can also create a new .artwork file by importing a directory of images:
#
#   ./iOS-artwork.py create -a original_artwork_file.artwork -d import_directory -c created_artwork_file.artwork
#
# Please see the README file for more details.

import os
import sys
from optparse import OptionParser

# import PIL.Image

from artwork.legacy_artwork_file import LegacyArtworkFile
from artwork.modern_artwork_file import ModernArtworkFile
    
COMMANDS = ["export", "create"]

def usage(parser):
    parser.print_help()
    sys.exit(-1)

def bail(message):
    print "\n%s\n" % message
    sys.exit(-1)

def file_extension(file_name):
    return os.path.splitext(file_name)[1][1:]
    
def action_export(artwork_file_name, directory):
    artwork_file = LegacyArtworkFile(artwork_file_name)
    if not artwork_file.is_legacy_supported:
        artwork_file = ModernArtworkFile(artwork_file_name)

    artwork_set = artwork_file.artwork_set    
    print "\nExporting %d images from %s (version %s)..." % (artwork_set.image_count, artwork_set.name, artwork_set.version)
    
    for artwork_image in artwork_set.iter_images():
        pil_image = artwork_image.get_pil_image()
        export_file_name = os.path.join(directory, artwork_image.retina_appropriate_name)
        pil_image.save(export_file_name, file_extension(export_file_name))
        print "\texported %s" % export_file_name
        
    print "\nDONE EXPORTING!"
    
# XXX TODO
# def action_create(artwork_file_name, directory, create_file_name, is_legacy):
#     artwork_binary = ArtworkBinaryFile(artwork_file_name)
#     if is_legacy:
#         set_info = get_legacy_artwork_set_info(artwork_file_name)
#     else:
#         set_info = artwork_binary.get_modern_artwork_set_info()
#     create_binary = WritableArtworkBinaryFile(create_file_name, artwork_binary)
#     create_binary.open()
    
#     print "\nCreating a new file named %s by importing %d images...\n\t(Using %s version %s as a template.)" % (create_file_name, set_info.image_count, set_info.name, set_info.version)
    
#     for image_info in set_info.iter_images():
#         #
#         # Grab the image from disk
#         #
#         pil_image_name = os.path.join(directory, image_info.name)
#         if not os.path.exists(pil_image_name):
#             create_binary.delete()
#             bail("FAIL. An image named %s was not found in directory %s" % (image_info.name, directory))
            
#         #
#         # Validate the image
#         #
#         try:
#             pil_image = PIL.Image.open(pil_image_name)
#         except IOError:
#             create_binary.delete()
#             bail("FAIL. The image file named %s was invalid or could not be read." % pil_image_name)
        
#         actual_width, actual_height = pil_image.size
#         if (actual_width != image_info.width) or (actual_height != image_info.height):
#             create_binary.delete()
#             bail("FAIL. The image file named %s should be %d x %d in size, but is actually %d x %d." % (pil_image_name, image_info.width, image_info.height, actual_width, actual_height))
        
#         try:
#             if (pil_image.mode != 'RGBA') and (pil_image.mode != 'RGB'):
#                 pil_image = pil_image.convert('RGBA')
#         except:
#             create_binary.delete()
#             bail("FAIL. The image file named %s could not be converted to a usable format." % pil_image_name)
        
#         #
#         # Write it
#         #
#         create_binary.write_pil_image(image_info, pil_image)
#         print "\timported %s" % image_info.name
    
#     create_binary.close()
    
#     print "\nDONE CREATING!"
    
def main(argv):
    #
    # Set up command-line options parser
    #
    parser = OptionParser(usage = """%prog [command] [parameters]

    export 
        -a artwork_file.artwork 
        -d export_directory
    
        Exports the contents of artwork_file.artwork as a set
        of images in the export_directory
    
    create  
        -a original_artwork_file.artwork 
        -d import_directory 
        -c created_artwork_file.artwork
         
        Imports the images found in import_directory into a new
        artwork file named created_artwork_file.artwork. Uses
        the original file for sizing and other information, but
        never writes to the original file.
    """)
    parser.add_option("-a", "--artwork", dest="artwork_file_name", help="Specify the input artwork file name. (Read-only.)", default = None)
    parser.add_option("-d", "--directory", dest="directory", help="Specify the directory to export images to/import images from.", default = None)
    parser.add_option("-c", "--create", dest="create_file_name", help="Specify the output artwork file name. (Write-only.)", default = None)

    #
    # Parse
    #
    (options, arguments) = parser.parse_args()
    
    #
    # Validate
    #
    if (len(arguments) != 1) or (options.artwork_file_name is None) or (options.directory is None):
        usage(parser)
        
    command = arguments[0].lower()
    if command not in COMMANDS:
        usage(parser)
        
    if (command == "create") and (options.create_file_name is None):
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

    if command == "export":
        action_export(abs_artwork_file_name, abs_directory)
    # elif command == "create":
    #     abs_create_file_name = os.path.abspath(options.create_file_name)
    #     if os.path.exists(abs_create_file_name):
    #         bail("Sorry, but the create file %s already exists." % options.create_file_name)
    #     action_create(abs_artwork_file_name, abs_directory, abs_create_file_name, is_legacy)
            
if __name__ == "__main__":
    main(sys.argv)
    

    
