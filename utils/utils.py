from os.path import isabs, dirname, abspath, isdir, join, normpath
import inspect

def get_abs_path(*dirs):
    """
    Return absolute path of a directory constructed by appending dirs one after another
    dirs are all directories under the module 'request_generator'.

    if the last dir of dirs provided has a '/', then no additional '/' is added.

    Ex: get_abs_path("dir1", "subdir") returns /home/user/Downloads/<module_name>/dir1/subdir/
    """
    #for relative path
    curr_filename = inspect.getframeinfo(inspect.currentframe()).filename
    curr_path = dirname(abspath(curr_filename))
    previous_path = join(curr_path, "../")
    previous_path = normpath(previous_path)
    curr_path = previous_path

    if dirs:
        for dir in dirs:
            curr_path = join(curr_path, dir)
    curr_path = join(curr_path,"")
    curr_path = normpath(curr_path)

    #return the current dir if it's a directory
    return curr_path