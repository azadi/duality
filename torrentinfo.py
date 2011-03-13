#! /usr/bin/env python

import sys
import os

try:
    import libtorrent as lt
except ImportError:
    sys.exit("The 'libtorrent' library is not installed")
    

def get_info(torrent_file):
    """Decode the BEncode data from a torrent file.
    
    Return size, total files, piece length, number of pieces and name.
    """
    
    try:
        torrent_info = lt.torrent_info(torrent_file)
    except RuntimeError:
        sys.exit('Invalid torrent file')
    
    # size of all the files in the torrent in bytes
    total_size = torrent_info.total_size()
    # the number of files in the torrent
    file_len = len(torrent_info.files())
    # the number of bytes for each piece
    piece_len = torrent_info.piece_length()
    # the total number of pieces
    num_pieces = torrent_info.num_pieces()
    # name of the torrent
    name = torrent_info.name()

    return total_size, file_len, piece_len, num_pieces, name


if __name__ == '__main__':

    if len(sys.argv) < 2:
        sys.exit("usage: torrentinfo.py <torrent-file>")
    if not os.path.isfile(sys.argv[1]):
        sys.exit("Invalid file {0}".format(sys.argv[1]))

    torrent_file = sys.argv[1]
    size, files, length, number, name = get_info(torrent_file)

    print "'{0}'".format(name)
    print '{0:.2f} MiB size,'.format(size / (1024.0 * 1024.00)),
    print '{0} files,'.format(files),
    print '{0} pieces,'.format(number),
    print '{0} bytes per piece.'.format(length)
