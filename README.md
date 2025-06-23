# iOS-artwork

### Forked from Jato-BZ's fork to add Python 3 support.

### Please note that creating an .artwork file has been disabled. Use the original fork instead.

You need the PIL (Pillow) library installed in order for this to function.

Make sure you clone the entire repository or the below command will not work.
Example command:

    python3 ./iOS_artwork.py export -a /path/to/artwork_file@2x.artwork -d /path/to/export_directory

## Original README.md below

### Forked originally from Dave Peck's GitHub and updated for iOS10 Support

The repo includes support for ALL iOS 6 - 10.X iconCache & dataclassIconCache .artwork files found in iOS

With the iOS 10 "@3x" .artwork files you will currently need to run the "artwork_hack.py" script over your file.
It creates a duplicate but removes the null padding Apple have applied to the @3x .artwork files. Essentially putting 
the iOS 10 @3x files back to iOS 9 specs.

Run the tool as follows:

    ./artwork_hack.py /path/to/artwork_file@3x.artwork

Then run this artwork extract tool as expected.

Dave Peck's original README below...

### An Important Note About iOS7

This tool is no longer supported.

June 18, 2013: This extractor tool is officially dead. It will not support `iOS7` or any future release of `iOS`. It will see no future updates for iOS6, either.

Without violating my NDA, `iOS7` introduces a new notion of "asset catalogs" which are managed by `XCode` and which are ultimately compiled down into `.car` files by the `actool` binary.

Asset catalogs in `iOS7` are radically different than the `.artwork` files found in previous versions of `iOS`. They contain images, yes, but they also contain complex metadata (like 3- and 9-grid slicing information), embedded fonts, paths, glyphs, icons, and a whole bunch of other stuff besides.

The bottom line: reverse-engineering these files is going to be a massive undertaking. More importantly, it may not be necessary anymore. Read on for details.

### What you should use instead of this tool.

If you want to extract the contents of `.car` files, you'll want to build a native iOS app that uses undocumented `UIKit` APIs to iterate through the available images. The best option right now is probably `0xced`'s [`UIKit-Artwork-Extractor`](https://github.com/0xced/UIKit-Artwork-Extractor) &mdash; I suspect we'll see it quickly updated for iOS7.

If you want to create _new_ `.car` files, you're in luck: just create an XCode 5 project, create an image catalog, and add your images to it. When you build your project, XCode5 will build a proper `.car` file for you.

Don't want to use XCode projects? No problem; inside the `XCode 5` app bundle is a binary called `actool` that is used to turn an image catalog into a `.car` file. You can `man actool` for more information; it's not terribly well documented, but I was able to get it to create simple and valid `.car` files.

It's worth pointing out some notable disadvantages to this approach over using my tool in the past:

1. You have to be a registered Apple developer in order to use these tools
2. The overall process of extracting images and then creating new archives _for the purposes of modding the iOS UI_ has gotten a lot more cumbersome. (Although a few shell scripts could theoretically help you here.)

### What you should know if you want to try reverse-engineering this stuff.

All this said, it *is* fundamentally possible to update my `iOS-artwork-tool` for `iOS7`. I just don't think it's worth it to do so, especially given that there are other tools that can accomplish similar goals.

If you feel like you're up to the challenge, here's what I know.

Under the hood, the `.car` file format is actually a Mac OS X BOM (Bill Of Materials) file.

Typical BOM files can be manipulated with the `lsbom` and `mkbom` command-line utilities. However, iOS7 `.car` files aren't typical BOM files. Standard BOM files contain a `Paths` variable in the BOM manifest; the `Paths` section is basically a directory tree.

While the new `.car` files are BOM files, they don't contain a `Paths` variable. Instead, they have ten unique variables, including `CARHEADER`, `RENDITIONS`, `COLORS`, `FONTS`, `FONTSIZES`, `GLYPHS`, `BEZELS`, `FACETKEYS`, `ELEMENT_INFO`, and `PART_INFO`. In order to properly support the new `*.car` files, you'll have to reverse-engineer each of these sections. The good news is that `actool` is quite capable of _creating_ content for each of these sections, so it should be possible to generate a number of handy example files from which you can then reverse-engineer the file layout.

One last "gotcha": the Mac OS X BOM file format is itself undocumented. Luckily, someone has taken a crack at it and has built a good-enough implementation of `lsbom` that you can at least get started on understanding the layout of the files. You can find this re-implementation at [cooljeanius/osxbom](https://github.com/cooljeanius/osxbom)

### Thanks for using the extractor throughout the years.

Lots and lots of people have used my extractor, and I really appreciate it!

But the time has come to move on to better tools and approaches. Godspeed, `iOS-artwork-extractor`... Godspeed.

-Dave


iOS Artwork Extractor for iOS6 and Earlier
==========================================

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


