#! /usr/bin/env python

# Joins individual parts downloaded by the Duality client.
# Written by Sukhbir Singh <www.duality.sukhbir.in>

import os
import sys
import glob
import hashlib

try:
    import libtorrent as lt
except ImportError:
    sys.exit("The 'libtorrent' library is not installed")


def return_range(lst):
    """Return range of consecutive numbers in a list."""
    return_list = []
    first = last = lst[0]
    for element in lst[1:]:
        # if the element is equal to the previous
        if element - 1 == last:
            # move on the next element
            last = element
        else:
            # if there is a single element, return that, else return a tuple
            return_list.append(first if (first==last) else (first, last))
            first = last = element
    return_list.append(first if (first==last) else (first, last))
    return return_list


def main(torrent_file):    
    """Read the torrent file and compare the individual parts."""
    # decode the torrent file
    info = lt.torrent_info(torrent_file)
    num_pieces = info.num_pieces()
    pieces_len = info.piece_length()
    info_hash = info.info_hash()

    print "Current working directory is '{0}'".format(os.getcwd())
    part_files = glob.glob('*.duality')
    config_files = glob.glob('*.config')

    num_part_files = len(part_files)
    num_config_files = len(config_files)
    message = 'Please ensure that your part and config files ' \
                                            'are in the current directory'
    if not num_part_files:
        sys.exit('No part files found\n{0}'.format(message))
    if not num_config_files:
        sys.exit('No config files found\n{0}'.format(message))

    # create a mapping of file name to a mapping of hash, lower and upper piece
    parts = {}
    for file_ in config_files[:]:
        with open(file_) as f:
            for line in f:
                config_info = line.split(',')
                name = config_info[0]
                hash_ = config_info[1]
                lower_piece = int(config_info[2])
                upper_piece = int(config_info[3])
                # Only add the key if the hash matches. This will help to filter
                # the other config or part files that are not related to the 
                # torrent file being merged, but are in the current working
                # directory. A simple but effective filter.
                if str(info_hash) == hash_:
                    parts[name] = dict(torrent_hash=hash_, 
                                        lower=lower_piece, 
                                        upper=upper_piece)
                else:
                    config_files.remove(file_)
   
    # if the file is not found 
    for files in parts.iterkeys():
        if not os.path.isfile(files):
            sys.exit('File: {0} not found'.format(files))

    # sort the dictionary by using the lower range as the key
    file_name = sorted(parts.iterkeys(), key= lambda k: parts[k]['lower'])
    # check whether we have the complete parts by comparing the range of pieces
    piece_count = []
    for each_file in file_name:
        for count in range(parts[each_file]['lower'], parts[each_file]['upper']+1):
            piece_count.append(count)

    # check for duplicate parts and notify the user. 
    duplicate_pieces = []
    for file_ in file_name:
        lower = parts[file_]['lower']
        upper = parts[file_]['upper']
        duplicate_pieces.extend(range(lower, upper))
    
    unique_elements = set(duplicate_pieces)
    # if the elements are not unique
    if len(duplicate_pieces) > len(unique_elements):
        sys.exit('Redundant pieces found. Please check your config files')

    # piece list from the torrent file
    torrent_pieces = set(range(0, num_pieces))
    # pieces in the torrent file but not in the part files
    missing_pieces = list(set(torrent_pieces) - set(piece_count))
    
    # If both lists are exactly the same, element by element, then proceed
    # otherwise quit. There is no hash comparison here, just the piece count is
    # checked, after all, if the piece count mismatches, why check the SHA-1.
    if not missing_pieces: 
        print 'All required parts found'
    else:
        print 'Error: Piece count mismatch'
        print 'The following pieces are missing:'
        missing_pieces = return_range(missing_pieces)
        for element in missing_pieces:
            if len(element) > 1:
                print '({0} - {1})'.format(element[0], element[1]),
            else:
                print '({0})'.format(element),
        sys.exit()

    print 'Matching hashes, please wait...'
    # get the piece SHA-1 hashes from the torrent file
    hashes = []
    for count in range(0, num_pieces):
        hashes.append(str(info.hash_for_piece(count)))

    piece_to_hash = []
    # get the SHA-1 hashes from the parts
    for file_ in file_name:
        f = open(file_, 'rb')
        for count in range(parts[file_]['lower'], parts[file_]['upper']+1):         
            temp_hash = hashlib.sha1()
            difference = (pieces_len * (count+1)) - pieces_len
            f.seek(difference)
            temp_hash.update(f.read(pieces_len))
            piece_to_hash.append(temp_hash.hexdigest())
            del temp_hash
        f.close()

    # now compare the hashes from the torrent file
    for item, hash_ in enumerate(hashes):
        if hash_ == piece_to_hash[item]:
            continue
        else:
            sys.exit('Error: hash mismatch for piece #{0}'.format(item))

    print 'All hashes match, file is complete\nMerging parts, please wait...'

    # get the name of the file from the torrent
    out_file_name = os.path.basename(info.files()[0].path)
    out_f = open(out_file_name, 'wb+')

    # file_name is the sorted list of part files
    pos = 0
    for file_ in file_name:
        with open(file_, 'rb') as f:
            # seek to the previous position
            f.seek(pos, 1)
            out_f.write(f.read())
            pos = f.tell()
            f.close()

    print 'Parts have been merged'
    print '{0} saved'.format(out_file_name)
    
    out_f.seek(0)
    # report the SHA-1 of the entire file, just to be very sure
    end_hash = hashlib.sha1()
    end_hash.update(out_f.read())
    print 'SHA-1 for the file is: {0}'.format(end_hash.hexdigest())

    # delete the config and part files
    print 'Delete part and config files for this torrent?'
    ask = raw_input('yes [default] / no: ')
    if ask in ('Y', 'y', 'yes', ''):
        for files_ in config_files:
            os.remove(files_)
        for files_ in parts.iterkeys():
            os.remove(files_)
        print 'Part and config files deleted'

    # all is well, thanks for using Duality!
    out_f.close()
    sys.exit('Goodbye!')


if __name__ == '__main__':

    if len(sys.argv) < 2:
        sys.exit("usage: joinit.py <torrent-file>")
    if not os.path.isfile(sys.argv[1]):
        sys.exit("Invalid torrent file {0}".format(sys.argv[1]))

    main(sys.argv[1])
