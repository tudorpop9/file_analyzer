import sys
import os, stat
import datetime as dt
import json
import itertools

scan_command = "scan"
query_command = "query"
read_only_flag = 0o444  # 100_100_100
read_only_mask = 0o777  # 111_111_111

cache_file_name = 'cache.json'

file_size_str = 'FileSize'
changed_str = 'Changed'
hidden_str = 'Hidden'
read_only_str = 'ReadOnly'


# transforma momentul ultimei modificari din secunde in formatul cerut
# operatia de max se face pentru a tine cont si de posibilele schimbari a meta-datelor
def get_modification_date(file_stats):
    modification_timestamp = max(file_stats.st_mtime, file_stats.st_ctime)

    modification_date = dt.datetime.fromtimestamp(modification_timestamp)
    formated_date = str(modification_date.year) + '/' \
                    + str(modification_date.month).zfill(2) + '/' \
                    + str(modification_date.day).zfill(2) + '-' \
                    + str(modification_date.hour).zfill(2) + ':' \
                    + str(modification_date.minute).zfill(2)

    return formated_date


# verifica daca un fisier e ascus pentru sistemul de operare windows
# pentru varianta doar cu directorul curent
def is_file_hidden_windows_dentry(dir_entry: os.DirEntry):
    hidden_flag = os.stat(dir_entry.path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN
    if hidden_flag != 0:
        hidden_flag = 1

    return hidden_flag


# verifica daca un fisier e ascus pentru sistemul de operare windows
# pentru varianta cu tot subtree-ul
def is_file_hidden_windows_fstat(file_stat: os.stat_result):
    hidden_flag = file_stat.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN
    if hidden_flag != 0:
        hidden_flag = 1

    return hidden_flag


# verific daca un fisier e ascus pentru un sistem de operare diferit de windows
# pt varianta in care verifica doar directorul curent
def is_file_hidden_other_dentry(dir_entry):
    return int(dir_entry.name.startswith('.'))

# verific daca un fisier e ascus pentru un sistem de operare diferit de windows
# pt varianta in care verifica subtree-urile
def is_file_hidden_other_fname(file_name):
    return int(file_name.startswith('.'))



# daca doar permisiunile de read sunt setate, operatia de 'and' cu o masca setata la 1 va fi 0o444
def is_file_read_only(file_st_mode):
    response = 0
    if (read_only_mask & file_st_mode) == read_only_flag:
        response = 1

    return response


# extragerea de infromatii despre fisierele din directorul curent
def scan_current_dir():
    file_dictionaries = dict()

    # detectarea fisierelor hidden difera la windows de alte OS-uri
    # if mai mare sa nu verific conditia de OS pentru fiecare fisier
    if sys.platform == 'win32':
        with os.scandir('./') as dir_iterator:
            for dir_entry in dir_iterator:
                if dir_entry.is_file():
                    file_stats = dir_entry.stat()

                    file_dictionaries[dir_entry.name] = {
                        file_size_str: file_stats.st_size,
                        changed_str: get_modification_date(file_stats),
                        hidden_str: is_file_hidden_windows_dentry(dir_entry),
                        read_only_str: is_file_read_only(file_stats.st_mode),
                    }
    else:
        with os.scandir('./') as dir_iterator:
            for dir_entry in dir_iterator:
                if dir_entry.is_file():
                    file_stats = dir_entry.stat()

                    file_dictionaries[dir_entry.name] = {
                        file_size_str: file_stats.st_size,
                        changed_str: get_modification_date(file_stats),
                        hidden_str: is_file_hidden_other_dentry(dir_entry),
                        read_only_str: is_file_read_only(file_stats.st_mode),
                    }

    # salvez informatiile despre fisiere
    with open(cache_file_name, 'w') as file:
        json.dump(file_dictionaries, file)


# extragerea de infromatii despre fisierele din directorul curent si a subdirectoarelor
def scan_current_dir_subtree():
    file_dictionaries = dict()
    file_paths = []
    file_names = []
    for root, dirs, files in os.walk('.'):
        for f_name in files:
            file_paths.append(str(os.path.join(root, f_name)))
            file_names.append(f_name)

    no_paths = len(file_paths)

    # detectarea fisierelor hidden difera la windows de alte OS-uri
    # if mai mare sa nu verific conditia de OS pentru fiecare fisier
    if sys.platform == 'win32':
        for idx in range(no_paths):
            file_stats = os.stat(file_paths[idx])

            file_dictionaries[file_names[idx]] = {
                file_size_str: file_stats.st_size,
                changed_str: get_modification_date(file_stats),
                hidden_str: is_file_hidden_windows_fstat(file_stats),
                read_only_str: is_file_read_only(file_stats.st_mode),
            }
    else:
        for idx in range(no_paths):
            file_stats = os.stat(file_paths[idx])

            file_dictionaries[file_names[idx]] = {
                file_size_str: file_stats.st_size,
                changed_str: get_modification_date(file_stats),
                hidden_str: is_file_hidden_other_fname(file_names[idx]),
                read_only_str: is_file_read_only(file_stats.st_mode),
            }

    # salvez informatiile despre fisiere
    with open(cache_file_name, 'w') as file:
        json.dump(file_dictionaries, file)


# https://www.geeksforgeeks.org/python-program-to-swap-two-elements-in-a-list/
def swap_elm(files, pos1, pos2):
    files[pos1], files[pos2] = files[pos2], files[pos1]
    return files


# functie care va muta elementul de valoarea minima pe prima pozitie a array-ului
def relocate_min(files):
    if len(files) < 1:
        return []

    for i in range(1, len(files)):
        if files[0]['size'] > files[i]['size']:
            files = swap_elm(files, 0, i)
    return files


# va returna primele 5 fisiere cu size-ul cel mai mare
def get_largest_files(file_informations: dict, no_files: int):
    largest_files = []
    # daca am <=5 elemente, acelea vor fi cele mai mari
    if no_files <= 5:
        for f in file_informations.keys():
            largest_files.append({
                'name': f,
                'size': file_informations[f][file_size_str]
            })
    # altfel, voi lua primele 5 elemente din toate fisierele
    else:
        for f in dict(itertools.islice(file_informations.items(), 5)).keys():
            largest_files.append({
                'name': f,
                'size': file_informations[f][file_size_str]
            })

        largest_files = relocate_min(largest_files)
        file_keys = list(file_informations.keys())

        for idx in range(5, no_files):
            current_file_size = file_informations[file_keys[idx]][file_size_str]

            # daca am detectat un file mai mare decat minimul din array pun noul element in locul lui
            # dupa care apelez functia care pune noul minim pe pozitia 0
            if current_file_size > largest_files[0]['size']:
                largest_files[0] = {
                    'name': file_keys[idx],
                    'size': current_file_size
                }
                largest_files = relocate_min(largest_files)

    # sortez rezultatul final
    sorted_largest_files = sorted(largest_files, key=lambda file: file['size'], reverse=True)
    return sorted_largest_files


# pretty print, atat
def get_top5_str(file_arr):
    size = len(file_arr)
    console_msg = "Top " + str(size) + " largest files: "
    for i in range(size):
        if i == size - 1:
            console_msg += file_arr[i]['name']
        else:
            console_msg += (file_arr[i]['name'] + ', ')

    return console_msg


def get_no_hidden_files(file_informations):
    no_hidden = 0
    for file_name in file_informations.keys():
        no_hidden += file_informations[file_name][hidden_str]
    return no_hidden


def get_no_readonly_files(file_informations):
    no_readonly = 0
    for file_name in file_informations.keys():
        no_readonly += file_informations[file_name][read_only_str]

    return no_readonly


# returneaza o lista cu fisierele modificate din fiecare luna(doar cele care apar)
def get_modified_files_freq(file_informations: dict):
    monthly_modification = dict()
    for file_info in file_informations.values():
        file_modification_month = file_info[changed_str][:7]  # len(YYYY/MM) = 7

        if file_modification_month not in monthly_modification:
            monthly_modification[file_modification_month] = 1
        else:
            monthly_modification[file_modification_month] += 1

    return monthly_modification


def query_function():
    # daca fisierul cache.json nu exista, va fi creat de scan_current_dir
    if not os.path.exists('./' + cache_file_name):
        # scan_current_dir()
        scan_current_dir_subtree()

    # incarc informatiile din fisier
    with open('./' + cache_file_name) as file:
        file_informations = json.load(file)

    # Cerinta I
    no_files = len(file_informations)
    print('Number of files: ' + str(no_files))

    # Cerinta II
    largest_files = get_largest_files(file_informations, no_files)
    print(get_top5_str(largest_files))

    # Cerinta III
    no_hidden_files = get_no_hidden_files(file_informations)
    percent_hidden = int((float(no_hidden_files) / float(no_files)) * 100.0)
    print(str(percent_hidden) + '% are hidden')

    # Cerinta IV
    no_readonly = get_no_readonly_files(file_informations)
    percent_readonly = int((float(no_readonly) / float(no_files)) * 100.0)
    print(str(percent_readonly) + '% are read-only')

    # Cerinta V
    monthly_modification_dict = get_modified_files_freq(file_informations)
    for month, no_modified_files in monthly_modification_dict.items():
        print(month + ': ' + str(no_modified_files) + ' modified files')


def main():
    arguments = sys.argv
    if len(arguments) < 2:
        pass
        # no command
    else:
        command = arguments[1]
        if command == scan_command:
            # scan_current_dir()
            scan_current_dir_subtree()
        elif command == query_command:
            query_function()
            pass
        else:
            print("Unknown command")


main()
