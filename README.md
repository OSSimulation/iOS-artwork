# iOS .artwork extractor

This repository supports ONLY extracting iPhoneOS 2.0 - 10.X? .artwork files, updated for Python 3.

Please note that the create function has been removed. [Use the original if you need that](https://github.com/cwalther/iphone-tidbits) (iPhoneOS 2.0 - iOS 6.1.6 only.)

You need the PIL (Pillow) library installed in order for this to function.

Make sure you clone the entire repository or the below command will not work. You cannot download the iOS_artwork.py file individually.
Example command:

    python3 ./iOS_artwork.py -a /path/to/artwork_file@2x.artwork -d /path/to/export_directory

For iOS 10 "@3x" files (not tested) you will need to run "artwork_hack.py" as well.
It creates a duplicate but removes the null padding Apple have applied to the @3x .artwork files; essentially turning 
the iOS 10 @3x files back to the iOS 9 spec.

Run this command, then run the above command as normal.

    python3 ./artwork_hack.py /path/to/artwork_file@3x.artwork
