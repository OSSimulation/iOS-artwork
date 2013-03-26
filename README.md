iOS Artwork Extractor
=====================

You may have noticed that most of Apple's iOS artwork is packaged in files ending with the `.artwork` extension. The iOS Artwork Tool makes it easy to export images from those files. Exporting is useful for certain iOS development tasks. The tool also supports creating *new* `.artwork` files from images that you've tweaked; this is useful if you want to create mods that change the basic appearance of the iPhone or iPad's interface.

With iOS6, this tool supports _all_ the SDK `.artwork` files! For SDKs prior to iOS6, only specific `.artwork` files are supported -- namely, all artwork referenced by `UIKit`, including shared artwork, Emoji artwork, and keyboard layout artwork.

### GET STARTED

The software is written in python. You must have Python 2.7 and the [Python Imaging Library](http://www.pythonware.com/products/pil/) installed in order for it to work. To do this, create a new `virtualenv`, activate it, and `pip install -r requirements.txt`.

Next, find the appropriate artwork files on disk. This tool supports iOS2 through iOS6. It's up to you to locate the `.artwork` files; if you're an Apple developer with the SDK, look in the Xcode app bundle.

### EXPORTING

To get the images out of a `.artwork` file, you *export* them. This fills a directory of your choosing with easily editable PNG files.

To export, run the tool as follows:

    ./iOS-artwork.py export -a /path/to/artwork_file.artwork -d /path/to/export_directory/

That's all there is to it!

### CREATING

It is equally easy to turn a directory full of PNGs into a new `.artwork` file.

To create a new `.artwork` file, run the tool as follows:

    ./iOS-artwork.py create -a /path/to/original_artwork_file.artwork -d /path/to/import_directory/ -c created_artwork_file.artwork

This will read all the PNGs in the `import_directory` directory and place them in the file named `created_artwork_file.artwork`. Again, easy!

You may wonder why you have to supply the *original* `.artwork` file in this example. That's because the images we import to the newly created `.artwork` must have the same dimensions and color space as the original -- otherwise iOS is likely to be unhappy with you.

### VERSION HISTORY

    v1.8 03/25/2013 - (CURRENT) Add support for AssistantMic-163r@1x~ipad.artwork -- found only on the iPad Mini firmware, not even in the SDK
    v1.7 02/05/2013 - Test support for iOS6.1, too. All is well.
    v1.6 12/13/2012 - Bugfix: properly handle iOS6 greyscale images. Their byte alignment is different.
    v1.5 09/21/2012 - Support iOS6.0.0! Major rewrite to support multiple styles of artwork file.
    v1.4 04/15/2012 - Support iOS 5.1
    v1.3 10/05/2011 - Support iOS 5!!!
    v1.2 10/04/2011 - fix major issues with premultiplied alpha and greyscale packaged images. support image flags. fix bugs in create.
    v1.1 08/21/2011 - fix problems with the 4.3.2 artwork files (and update them to 4.3.3)
    v1.0 07/07/2011 - support iOS 4.3. support Emoji files.
    v0.9 12/06/2010 - massive rewrite to support iOS 4.2.1 files. Totally new generator script based on cracking mach-o files.
    v0.8 09/13/2010 - support iPhone OS 4.1.0 and 3.2.0 artwork files.
    v0.7 12/07/2008 - support iPhone OS 2.2.0 artwork files from UIKit
    v0.6 07/28/2008 - support other image formats besides RGBA. Fix a filename-related bug (used relative name instead of absolute.)
    v0.5 07/25/2008 - add support for MobilePhone images, and clean up usage messages.
    v0.4 07/24/2008 - add feature support for -import so that you can make artwork files
    v0.3 07/19/2008 - use os.path to manipulate paths so that things work nicely on windows
    v0.2 07/18/2008 - change command line structure to use -export (preparing to also add -import) and fix bugs in usage_* methods
    v0.1 07/13/2008 - released initial version, with export support for all 2.0.0 UIKit artwork

### Contact Me

Feel free to send comments, suggestions, and improvements my way. See code comments for details on making improvements. You can find my email address in the information area below.

### What's in this directory?

The `iOS-artwork.py` script is the main workhorse here. It's the only thing you'll want to use.

The `generate-legacy-metadata.py` script is a helper that is capable of reading structs from SDK Mach-O binaries, such as `UIKit`, and finding appropriate symbols and offsets for images. You shouldn't use this.

The `legacy_metadata` directory contains a bunch of JSON files that have metadata about supported `.artwork` files and the images they contain. There's a `README` in there that explains more: as the name implies, this directory only contains metadata for "legacy"-style `.artwork` files. Modern `.artwork` files found in iOS6 don't need this metadata because the `.artwork` files themselves contain it.

Finally, the `artwork` directory is a Python package that contains most of the interesting code for making things work.

### What happened to all the old stuff that used to be part of this repo?

I used to have a bunch of other random stuff in this repo, like tools to help with reading/writing streaming binary data in Objective-C. Most of those bits of code were old and crufty, written in the iOS3 era and in definite need of attention. I axed them, although you can find them if you go back through the `git` history.


