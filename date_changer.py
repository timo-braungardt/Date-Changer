import argparse
import datetime
import os
import piexif



####### setup of the argument parser #######

'''date_changer -p [path] -o [photo] -t [actual timestamp of the photo]'''

parser = argparse.ArgumentParser(description='Correct the timestamp of photos')
parser.add_argument('-p', '--Path', help='Path to the pictures. If empty, current dir will be used.', action='store', dest='path', default='./')
requiredArg = parser.add_argument_group('required arguments')
requiredArg.add_argument('-o', '--Old', help='Picture with the old timestamp. (only name, no path)', action='store', dest='old_timestamp', required=True)
requiredArg.add_argument('-t', '--Time', help='Actual timestamp of the picture as YYYY:MM:DD-hh:mm:ss', action='store', dest='new_timestamp', required=True)

args = parser.parse_args()



####### methods #######

def _get_time(path):
    '''
    Reads the exif of the path and returns DateTimeOriginal as datetime object
    '''
    exif = piexif.load(path)

    # get DateTimeOriginal
    date = exif['Exif'][36867]
    date = date.decode('UTF-8')

    return datetime.datetime.strptime(date, "%Y:%m:%d %H:%M:%S")

def _set_time(path, time):
    '''
    Sets the datetime to an existing file
    '''
    exif = piexif.load(path)

    stringtime = time.strftime("%Y:%m:%d %H:%M:%S")
    stringtime = stringtime.encode('UTF-8')

    # set DateTimeOriginal and DateTimeDigitized
    exif['Exif'][36867] = stringtime
    #exif['Exif'][36868] = stringtime      # uncomment if your enjoy the tingle of no return

    binarydump = piexif.dump(exif)
    piexif.insert(binarydump, path)



####### main #######

if __name__ == '__main__':
    # check dir
    if not os.path.isdir(args.path):
        raise OSError(f'Path {args.path} can\'t be found')

    # check file
    old_timestamp = args.path + args.old_timestamp
    if not os.path.isfile(old_timestamp):
        raise OSError(f'File {old_timestamp} can\'t be found')

    # check time
    try:
        new_timestamp = datetime.datetime.strptime(args.new_timestamp, "%Y:%m:%d-%H:%M:%S")
    
    except ValueError:
        raise ValueError(f'The timestamp {args.new_timestamp} is wrong. It has to be YYYY:MM:DD-hh:mm:ss')



    # calculate offset
    old_timestamp = _get_time(args.path + args.old_timestamp)
    offset = new_timestamp - old_timestamp

    # get all pictures
    included_extensions = ['jpg','jpeg', 'JPG', 'JPEG']
    pictures = [fn for fn in os.listdir(args.path)
        if any(fn.endswith(ext) for ext in included_extensions)]

    # ask again
    print(f'Dates will be changed by {offset}')
    print(f'{len(pictures)} file(s) will be affected')
    print(f'Are you sure? (Y): ',  end='')
    response = input()
    response = response.lower()

    if response != 'y':
        # close without an error
        print('aborted.')
        exit(0)

    #advance and change the timestamps
    for i in range(len(pictures)):
        print(f'Picture {i} of {len(pictures)}')

        file = args.path + pictures[i]

        time = _get_time(file)
        time = time + offset
        _set_time(file, time)

    print(f'Picture {len(pictures)} of {len(pictures)}')
    print('finished!')
