#! /usr/bin/env python

# Duality BitTorrent Client
# Written by Sukhbir Singh <www.duality.sukhbir.in>
# The README file has more information on how this works.

import sys
import os
import time

try:
    import libtorrent as lt
except ImportError:
    sys.exit("The 'libtorrent' library is not installed")


def configuration_writer(info_hash, lower, upper, name, f_name):
    """Write the configuration file that will be used for joining the file parts.

    info_hash returns the SHA-1 hash for the info-section of the torrent file.
    This is used to identify a torrent file, as the hash is unique. lower and
    upper specify the piece range, they will be also written to the file to
    make joining easier as there will be multiple parts to join. f_name
    is the modified name of the file that will be saved.

    """
    file_name = '{0}.{1}-{2}.config'.format(name[:10], lower, upper)
    with open(file_name, 'w') as f:
        f.write('{0},{1},{2},{3}'.format(f_name, info_hash, lower, upper))


def main(torrent_file):
    # get the torrent info from the file
    try:
        info = lt.torrent_info(torrent_file)
    except RuntimeError:
        sys.exit('Invalid torrent file')

    # file_len - number of files in the torrent
    # piece_len - number of bytes / piece
    # num_pieces - number of pieces
    # name - name of the torrent
    file_len = len(info.files())
    piece_len = info.piece_length()
    num_pieces = info.num_pieces()
    name = info.name()

    # support for multiple files to be added later
    if file_len > 1:
        print 'WARNING!\nThis torrent has more than one file to be' \
                ' downloaded.\nThere is NO support for multiple files.'
        sys.exit('Please use a torrent with a single file.')


    down_size = (info.total_size() / (1024.0 * 1024.0))
    print "\n'{0}'\n{1} pieces ({2:.2f} MiB)".format(name, num_pieces, down_size)

    # ask the user to set the download rate
    try:
        download_rate = int(raw_input('Download rate limit (kB) '
                                                    '[default is infinite]: ') or 0)
        download_rate *= 1000
    except ValueError:
        download_rate = 0
    if download_rate < 0:
        download_rate = 0

    # the piece download range [lower, upper]
    print '(Piece range)'
    while True:
        try:
            lower = int(raw_input('Lower (> 0): ') or 0)
        except ValueError:
            continue
        if lower not in range(0, num_pieces):
            continue
        break
    while True: 
        try:
            upper = int(raw_input('Upper (< {0}): '.format(num_pieces-1)) or num_pieces-1)
        except ValueError:
            continue
        if upper not in range(0, num_pieces):
            continue
        if lower > upper:
            print 'Error: Lower range is greater than upper range'
            continue
        break

    pieces_download = (upper + 1) - lower
    piece_size = pieces_download * piece_len / (1024.0 ** 2)
    print '({0} pieces, {1:.2f} MiB)'.format(pieces_download, piece_size) 
    
    # get the filename from the torrent and modify it
    filename = os.path.basename(info.files()[0].path)
    new_filename = '{0}.{1}-{2}.duality'.format(filename, lower, upper)
    # now change the name of the file that will be downloaded
    info.rename_file(0, new_filename)

    # save the configuration file that will be used for joining the file parts
    configuration_writer(info.info_hash(), lower, upper, name, new_filename)
   
    # initiate the session
    session = lt.session()
    # port range to listen
    session.listen_on(6881, 6891)
    session.set_download_rate_limit(download_rate)
    handle = session.add_torrent({'ti': info, 'save_path': '.'})
   
    # Set the priority of pieces outside the range of [lower, upper] to 0. 0 priority
    # means that the piece is not downloaded. This is done in two steps, first, from 
    # 0 (first piece) to 'lower', then from 'upper'+1 to total number of pieces+1. So
    # only the pieces within this range will be downloaded. 
    for pieces_download in range(0, lower):
        handle.piece_priority(pieces_download, 0)
    for pieces_download in range(upper+1, num_pieces+1):
        handle.piece_priority(pieces_download, 0)

    while (not handle.is_seed()):
        status = handle.status()
        print ("\rDownloading: {0:.2f}%" 
        " [{1:.1f} down {3:.1f} up (kb/sec), {2} peers]").format(
                                                    status.progress * 100, 
                                                    status.download_rate / 1000,
                                                    status.num_peers,
                                                    status.upload_rate / 1000),
        sys.stdout.flush()
        # handle.is_seed won't work as we are not downloading the complete
        # file(s). So we check with the progress explicitly.
        if int(status.progress) == 1:
            break
        time.sleep(1)

    sys.exit('Download completed!')

    
if __name__ == '__main__':

    if len(sys.argv) < 2:
        sys.exit("usage: client.py <torrent-file>")
    if not os.path.isfile(sys.argv[1]):
        sys.exit("Invalid file {0}".format(sys.argv[1]))

    torrent_file = sys.argv[1]
    main(torrent_file)
