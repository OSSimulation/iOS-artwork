#!/usr/bin/env python

import struct
import os
import os.path
import sys

def main():
    
    cwd = os.getcwd() 
    artwork_file_path = sys.argv[1] 
    path, file = os.path.split(artwork_file_path)
    artwork_file = open(artwork_file_path, 'rb')
    artwork_file_data = artwork_file.read()
    artwork_file_data_size = len(artwork_file_data)
    artwork_file_magic = "\x91\x32\xA4\xCB"
    new_artwork_file_magic = "\xA2\x43\xB5\xDC"
    #
    # Read end of file footer for image size and artwork magic
    #
    image_size = struct.unpack('<L', artwork_file_data[(artwork_file_data_size - 16):(artwork_file_data_size - 12)])[0]
    artwork_magic = artwork_file_data[(artwork_file_data_size - 4):(artwork_file_data_size)]
    #
    # Exit tool if not a valid .artwork file
    #
    if artwork_magic == artwork_file_magic:
        
        pass

    elif artwork_magic == new_artwork_file_magic:

        pass

    else:

        print("\n%s is not a valid .artwork file!!!" % file)
        sys.exit()
    #
    # Work out from the icon image size declared in the .artwork file if @1x,@2x or @3x type .artwork file.
    #
    if image_size == 29:

        artwork_type = "\"Non Retina\" - @1x"

    elif image_size == 58:

        artwork_type = "\"Retina\" - @2x"

    else:

        pass
    #
    # Create IF statement to exit tool if image size does not match 87px for @3x icons
    #
    if image_size == 87:
        #
        # Add IF statement to exit tool if iOS 8 - 9.2.1 .artwork magic does not match new_artwork_file_magic
        #
        if artwork_magic == new_artwork_file_magic:
            #
            # Read end of file footer for total icon count
            #
            total_icon_count = struct.unpack('<L', artwork_file_data[(artwork_file_data_size - 8):(artwork_file_data_size - 4)])[0]        

            artwork_file.seek(0)
            pos = artwork_file.tell()
            #
            # Check to see if the new file to be created already exists
            #
            if os.path.isfile(file):

                print("\nFAIL. %s already exists -- don't want to overwrite it." % (file))
                artwork_file.close()
                exit()

            else:
                #
                # Create new artwork file
                #
                new_artwork_file_header = "%s" % (file)
                new_artwork_file = open(new_artwork_file_header, 'wb')  



            icon_count = 1
            row_count = 1
            total_bytes = 0
            #
            # Iterate over the original .artwork file while icon count is less than total icon count
            # Write png data minus the 32 byte icon row padding
            # 
            while icon_count <= total_icon_count:

                if row_count == 88:

                    row_count = 1
                    icon_pad = artwork_file_data[pos:pos + 2144]
                    new_artwork_file.write(icon_pad)
                    pos += 3456
                    icon_count += 1
                    total_bytes += 4096
                    #
                    # 87 x 32 = 2784 bytes
                    # total pad = 3456 then minus 2144 (iOS8 pad is 2144) = 1312
                    #
                    # Add IF statement to subtract the typical end icon padding for the last icon
                    #
                    if icon_count == total_icon_count:
                
                        total_bytes += -1312

                    else:
                
                        pass
            
                else:
    
                    pass
                #
                # Write data to new artwork file minus the 32 byte pad Apple have applied
                #
                short_bytes = artwork_file_data[pos:pos + 352]
                new_artwork_file.write(short_bytes)
                pos += 384
                row_count += 1
  
            artwork_file.close()
            new_artwork_file.close()
            #
            # Grabbing new file size total bytes
            #
            new_artwork_file = open(new_artwork_file_header, 'rb')
            new_artwork_file_data = new_artwork_file.read()
            total_bytes_new_artwork = len(new_artwork_file_data)

            print("\n%s created using %s as a template" % (new_artwork_file_header, artwork_file_path))
            print("\nOriginal file size: %d" % artwork_file_data_size)
            print("Total bytes skipped: %d" % total_bytes)            
            print("New file size: %d" % total_bytes_new_artwork)

        else:

            artwork_file.close()
            print("\nThis tool does not support iOS 8 - 9.2.1 @3x type files -- as not required.")    

    else:
        
        artwork_file.close()
        print("\nThis tool does not support %s type files -- as not required." % (artwork_type))

if __name__ == "__main__":
    main()
