image-folder-diff
=================

Script to help find missing and moved image files.  This is a personal tools I use to manage my images.  I hope you find good use of this tool.

Released as free software with a BSD style license (see LICENSE below).

EXAMPLES
========
> image-folder-diff.py --help
    List all options and brief explanation on usage.

> image-folder-diff.py missing source-folder dest-folder
    Lists all files in source folder that are not in test folder.

> image-folder-diff.py savedb source-folder source.ifd
    Stores all file metadata in a file, this means you can show differences between dates or on different devices easily.

> image-folder-diff.py missing yesterday.ifd picture-folder
    Show what files have been removed since yesterday.

> image-folder-diff.py missing -v pictures backup
    Show difference with verbose information, e.g. renamed files.


LICENSE
=======

Copyright (c) 2012, Sverrir Á. Berg <sab@keilir.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
Redistribution of source code must retain the above copyright notice, this list of conditions and the following disclaimer. Redistribution in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.  Neither the name of the copyright holder nor the names of contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.