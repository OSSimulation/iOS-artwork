Legacy Metadata
===============

## What's this about?

In iOS6, Apple introduced a new, completely self-contained format for its `*.artwork` files.

_Prior_ to iOS6, the information necessary to determine what images were in the `*.artwork` files wasn't found in the artwork files themselves: it was found in a motley assortment of framework binaries. For example, the `UIKit` binary contained an (unexported) symbol that, if you figured out its structure, could tell you the offsets, names, sizes, and colorspaces of the artwork pixels in several related `*.artwork` files.

So: prior to iOS6, I had a (now retired, but you can find it in the git repo's history) script called `generate-from-macho-binary.py` that could crack a framework binary like `UIKit` to figure out what `*.artwork` files it knew about.

Since it was a pain to use `generate-from-macho-binary.py`, I ended up having it output a `json` file for each known `*.artwork` file with the relevant information: image names, sizes, offsets, etc.

This directory contains metadata all the `*.artwork` files that my tool knows about for iOS3 through iOS5. 

Thankfully, this nonsense is no longer necessary with iOS6. With any luck, it won't be necessary with iOS7, either!


