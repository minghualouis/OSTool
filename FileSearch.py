import os
import re
import datetime
from queue import Queue


search_help_str = """
    Search allows you to look in a given directory.
    With out a search criteria it lists all files in
    the directory
    search params:
        -dir <directory>  -> the directory to search in (not including it will search the current directory)
        -r -> search recursively (delve into sub folders of the root directory)
        -pattern[:regex|:literal] <text> -> select only files with the given regex or literal string in their name
                                            (if you use both regex and literal, the filensme/file content only needs to
                                            match one)
        -inFile -> if a regex or literal is provided the program will search for the literal inside the file
                    as well as in it's name (only works on a line by line basis).
        -moded[:before|:after] yyyy[-mm[-dd[ HH[:MM[:SS]]]]] -> select only files that were modified before/
                                                            after the given date-time, if a before and after are given,
                                                            only files between the dates are selected, only an input
                                                            year is required, but more specific date-times are allowed
        -wrt <file> -> write output to the given file instead of to the console.
        -exit -> end search loop
"""


def search_loop():
    params = dict()
    search_help()
    while 'exit' not in params:
        params_str = input('input:')
        params = search_parse_params(params_str)
        if 'exit' in params.keys():
            break
        if 'bad' in params.keys():
            search_help()
            continue
        if 'write_to' in params.keys():
            search_to_file(params)
        else:
            search(params)


def search_help():
    print(search_help_str)


def search_parse_params(params_str):
    """
    parse the given string into the params dictionary,
    :param params_str:
    :return: the params dictionary
    """
    parts = params_str.split()
    params = dict()

    # search the current directory by default, the only required parameter
    params['directory'] = os.getcwd()

    # parse the optional parameters
    i = 0
    while i < len(parts):
        # param to search children folders recursively
        if parts[i] == "-r":
            params['recursive'] = True
        elif parts[i] == '-inFile':
            params['inFile'] = True
        # param to quit searching the file system
        elif parts[i] == '-exit':
            params['exit'] = True
        # param to write output to a given file
        elif parts[i] == '-wrt':
            i += 1
            if i < len(parts):
                params['write_to'] = parts[i]
            else:
                params['bad'] = True

        # param to only include files that match a given regular expression
        elif parts[i] == '-pattern:regex':
            i += 1
            if i < len(parts):
                re.compile(parts[i])
                params['regex'] = parts[i]

            else:
                params['bad'] = True

        # param to only include files that contain a given literal string
        elif parts[i] == '-pattern:literal':
            i += 1
            if i < len(parts):
                params['literal'] = parts[i]
            else:
                params['bad'] = True

        # param to only include files moded before a specific date
        elif parts[i] == '-moded:before':
            i += 1
            if i < len(parts):
                params['before'] = parse_time(parts[i])
                if params['before'] is None:
                    params['bad'] = True
            else:
                params['bad'] = True

        # param to only include files moded after a specific date
        elif parts[i] == '-moded:after':
            i += 1
            if i < len(parts):
                params['after'] = parse_time(parts[i])
                if params['after'] is None:
                    params['bad'] = True
            else:
                params['bad'] = True

        # param to search from a given directory (instead of the current directory)
        elif parts[i] == "-dir":
            i += 1
            if i < len(parts):
                possible_dir = parts[i]
                if not possible_dir.endswith(os.path.sep):
                    possible_dir += os.path.sep
                if os.path.isdir(possible_dir):
                    params['directory'] = possible_dir
                else:
                    params['bad'] = True
            else:
                params['bad'] = True

        # anything else is an invalid parameter
        else:
            params['bad'] = True
        i += 1
    return params


def parse_time(time_str):
    """
    Parse a string into a date time, that's formatted:
    'YYYY-mm-DD:HH:MM:SS:fffffff' everything after the year is optional,
    though, to specify day, you must first specify month, and similar
    with following specifcity of the datetime.
    :param time_str:
    :return: the datetime parsed out, or None if the string doesn't match a datetime
    """
    l = len(time_str)
    if l == 4:  # years
        return datetime.datetime.strptime(time_str, '%Y')
    if l == 7:
        return datetime.datetime.strptime(time_str, '%Y-%m')
    if l == 10:
        return datetime.datetime.strptime(time_str, '%Y-%m-%d')
    if l == 13:
        return datetime.datetime.strptime(time_str, '%Y-%m-%d:%H')
    if l == 16:
        return datetime.datetime.strptime(time_str, '%Y-%m-%d:%H:%M')
    if l == 19:
        return datetime.datetime.strptime(time_str, '%Y-%m-%d:%H:%M:%S')
    return None


def search(params):
    """
    Search the directory marked in params, and print the file name, date, and size,
    if it matches the other given parameters
    :param params: a dictionary of parameters
    :return: None
    """

    print("Filename\tmodification date\tfile size")
    q = Queue()
    root = params['directory']
    q.put(root)
    if valid_file(root, params):
        print(file_info(root))

    while not q.empty():
        cur_dir = q.get()
        if not cur_dir.endswith(os.path.sep):
            cur_dir += os.path.sep

        try:
            for filename in os.listdir(cur_dir):
                cur_file = cur_dir + filename
                if 'recursive' in params.keys() and os.path.isdir(cur_file):
                    if cur_file.endswith(os.path.sep):
                        cur_file += os.path.sep
                    q.put(cur_file)

                if valid_file(cur_file, params):
                    print(file_info(cur_file))
        except PermissionError:
            print("Cannot open: " + cur_dir)


def valid_file(filename, params):
    """
    Checks if a file matches the search criteria in the params dict
    (if the file was last moded before/after given datetimes, and if the
    filename or text inside contains the given literal or a string that matches
    the given regex).
    :param filename: the name of the file/directory to search
    :param params: a dictionary with possible search criteria optional criteria is the
    'before' & 'after' datetimes, and the 'literal' and 'regex' string searches, the 'inFile'
    criteria will apply the search to inside the file
    :return: True if the file matches the given input params, else false
    """

    valid = True
    if 'before' in params.keys() or 'after' in params.keys():
        file_date = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
        if 'before' in params.keys():
            valid &= file_date <= params['before']
        if 'after' in params.keys():
            valid &= file_date >= params['after']

    if 'literal' in params.keys() or 'regex' in params.keys():
        if 'inFile' in params.keys() and os.path.isfile(filename):
            valid &= test_file(filename, params)
        else:
            valid &= test_string(filename, params)
    return valid


def test_string(str, params):
    if 'literal' in params.keys() and params['literal'] in str:
        return True
    if 'regex' in params.keys() and re.search(params['regex'], str):
        return True
    return False


def test_file(file, params):
    if test_string(file, params):
        return True
    with open(file, encoding='utf-8') as reading:
        try:
            for line in reading:
                if test_string(line, params):
                    return True
        except UnicodeDecodeError:
            return False
    return False


def time_string(time_float):
    t = datetime.datetime.fromtimestamp(time_float)
    return t.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def memory_String(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def file_info(filename):
    #TODO make parsers for different file types to better search inside, only plain text utf-8 works currently
    ret = filename
    if os.path.isfile(filename):
        ret += "\t" + time_string(os.path.getmtime(filename)) + "\t" + memory_String(os.path.getsize(filename))
    elif os.path.isdir(filename):
        ret += "\t" + time_string(os.path.getmtime(filename))
    else:
        ret += "\tNot File or Directory"
    return ret


def search_to_file(params):
    with open(params['write_to'], 'w') as output:

        output.write("Filename\tmodification date\tfile size\n")
        q = Queue()
        root = params['directory']
        q.put(root)
        if valid_file(root, params):
            output.write(file_info(root) + '\n')

        while not q.empty():
            cur_dir = q.get()
            if not cur_dir.endswith(os.path.sep):
                cur_dir += os.path.sep

            try:
                for filename in os.listdir(cur_dir):
                    cur_file = cur_dir + filename
                    if 'recursive' in params.keys() and os.path.isdir(cur_file):
                        if cur_file.endswith(os.path.sep):
                            cur_file += os.path.sep
                        q.put(cur_file)

                    if valid_file(cur_file, params):
                        output.write(file_info(cur_file) + '\n')
            except PermissionError:
                output.write("Cannot open: " + cur_dir + '\n')


# sample search string query
r'''
-wrt output.txt -pattern:literal banana -moded:before 2017-03-01 -moded:after 2017-02-01 -inFile -r -dir C:\Users\mboni\OneDrive\Stories
'''

