from collections import defaultdict

import argparse
import binascii
import cPickle
import logging
import os

__author__ = "Sverrir A. Berg <sab@keilir.com>"


def FileCRC(filename):
    crc = 0
    with open(filename,'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 8192), ''):
             crc = binascii.crc32(chunk, crc)
    return 0xffffffff & crc


class FolderWrapper(object):
    def __init__(self, path):
        assert os.path.isdir(path)
        self._path = path
        self.__normpath = os.path.normpath(path).lower()

    def path(self):
        return self._path

    def norm_path(self):
        return self.__normpath


class FileWrapper(object):
    def __init__(self, fow, path):
        assert not os.path.isabs(path)
        self._fow = fow
        self._path = path
        self.__normpath = None
        self.__fullpath = None
        self.__size = None
        self.__crc = None

    def path(self):
        return self._path

    def full_path(self):
        if self.__fullpath is None:
            logging.debug("Calculating full_path for %s", self._path)
            self.__fullpath = os.path.normpath(os.path.join(self._fow.path(), self._path))
        return self.__fullpath

    def norm_path(self):
        if self.__normpath is None:
            logging.debug("Calculating norm_path for %s", self._path)
            self.__normpath = os.path.normpath(self._path).lower()
        return self.__normpath

    def size(self):
        if self.__size is None:
            logging.debug("Fetching size of %s", self._path)
            self.__size = os.path.getsize(self.full_path())
        return self.__size

    def crc(self):
        if self.__crc is None:
            logging.debug("Calculating CRC of %s", self._path)
            self.__crc = FileCRC(self.full_path())
        return self.__crc

    def same_as(self, fiw, crc=False):
        if self.size() == fiw.size():
            if crc:
                if self.crc() == fiw.crc():
                    return True
            else:
                return True
        return False

    def populate(self):
        """
            Fully populate all internal fields.
        """
        self.full_path()
        self.norm_path()
        self.size()
        self.crc()

    def __str__(self):
        return "[File '%s' in folder '%s']" % (self.__normpath, self._fow.norm_path())


class FolderScanner(object):
    def __init__(self, folder):
        self._folder = folder
        self._scanned = False
        self._is_db = False
        self._files = []
        self._paths = defaultdict(list)
        self._norm_paths = defaultdict(list)
        logging.debug("FolderScanner: '%s'", folder)
        if not os.path.isdir(folder):
            # Make sure this is a db file:
            p,ext = os.path.splitext(folder)
            if ext != ".ifd":
                logging.warning("'%s' is not a folder or a file with .ifd ending!", folder)
                exit(1)
            self._is_db = True

    def files(self):
        self.scan()
        return self._files

    def paths(self):
        self.scan()
        return self._paths.keys()

    def norm_paths(self):
        self.scan()
        return self._norm_paths.keys()

    def norm_path_files(self, norm_path):
        self.scan()
        return self._norm_paths.get(norm_path, [])

    def scan(self, full=False):
        if full and self._scanned:
            logging.warning("FileObject full scan requested after a scan has been performed!")
        if not self._scanned:
            if self._is_db:
                self._read_db()
            else:
                self._scan_folder(full)
            self._scanned = True

    def _scan_folder(self, full=False):
        for dir_path, dir_names, file_names in os.walk(unicode(self._folder)):
            fow = FolderWrapper(dir_path)
            for filename in file_names:
                fiw = FileWrapper(fow, filename)
                if full:
                    fiw.populate()
                self._add_fiw(fiw)

    def _add_fiw(self, fiw):
        self._files.append(fiw)
        self._paths[fiw.path()].append(fiw)
        self._norm_paths[fiw.norm_path()].append(fiw)
        if len(self._files) % 100 == 0:
            logging.info("Scanned %d files", len(self._files))

    def save_db(self, folder_scanner):
        self.scan()
        with open(folder_scanner._folder, "wb") as f:
            cPickle.dump(self._files, f, cPickle.HIGHEST_PROTOCOL)

    def _read_db(self):
        with open(self._folder, "rb") as f:
            files = cPickle.load(f)
            for file in files:
                self._add_fiw(file)

def missing(s, d, crc):
    dest_norm_paths = d.norm_paths()
    not_found = []
    for file in s.files():
        if file.norm_path() not in dest_norm_paths:
            logging.debug("%s not in dest", file)
            not_found.append(file)
        else:
            found_match = False
            for candidate in d.norm_path_files(file.norm_path()):
                if file.same_as(candidate, crc):
                    logging.debug("%s found in dest", file)
                    found_match = True
                    break
            if not found_match:
                logging.debug("%s not in dest (file(s) with same name found though", file)
                not_found.append(file)

    renamed = []
    for file in not_found:
        logging.info("Trying to find renamed/moved file %s", file.full_path())
        found_match = False
        for df in d.files():
            if file.same_as(df):
                logging.info("%s renamed/moved to %s", file.full_path(), df.full_path())
                found_match = True
                break
        if found_match:
            renamed.append(file)

    for file in renamed:
        logging.debug("Removing from not_found list: %s", file.full_path())
        not_found.remove(file)

    if len(not_found) == 0:
        print "All files in Source are in Dest folder"
    else:
        print "Listing %d file(s) in Source that are missing/different in Dest folder (%d scanned):" % (len(not_found), len(s.files()))
        for file in not_found:
            print file.full_path()


def save_db(s, d):
    s.scan(full=True)
    s.save_db(d)


def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.WARN)

    parser = argparse.ArgumentParser(description="Shows difference between two folders containing image files")
    parser.add_argument("action", choices=["missing", "savedb"], help="What action to perform")
    parser.add_argument("source", help="Source folder (or source.ifd)")
    parser.add_argument("dest", help="Destination folder (or dest.ifd)")
    parser.add_argument("-c", "--crc", action="store_true", help="If you want to CRC check as well as size check")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="")

    args = parser.parse_args()
    if args.verbose > 1:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose > 0:
        logging.getLogger().setLevel(logging.INFO)

    logging.debug("Starting")
    logging.info("Action: %s", args.action)
    logging.info("Source: %s", args.source)
    logging.info("Dest:   %s", args.dest)

    s = FolderScanner(args.source)
    d = FolderScanner(args.dest)

    if args.action == "missing":
        missing(s, d, args.crc)
    elif args.action == "savedb":
        save_db(s, d)
    else:
        logging.error("Invalid action")

    logging.debug("Done")


if __name__ == "__main__":
    main()