import os
import shutil
import re
import glob

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def write_file(content, dst_path):
    with open(dst_path, 'w', encoding='utf-8') as file:
        file.write(content)

def read_mdx(mdx_path):
    pass


def count_strings(content):
    print(len(content))


def copy_md_files_with_numeric_prefix(src_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.md'):
                if re.match(r'^\d+', file):
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_dir, file)
                    shutil.copy(src_file, dest_file)


def find_md_files_with_numeric_prefix(path):
    all_numeric_md_path = []
    for root, dirs, files in os.walk(os.path.normpath(path)):
        for file in files:
            if file.endswith('.md'):
                if re.match(r'^\d+', file):
                    all_numeric_md_path.append(os.path.join(root, file))




def find_md_files(root_dir):
    md_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in glob.glob(os.path.join(dirpath, '*.md')):
            md_files.append(filename)

    return md_files


def recover_ol_md_path(path):
    # print(path)
    md_path_split = path.split('/')[1:]
    # print(md_path_split)
    if len(md_path_split) == 1:
        md_dir = ''
        len_dir = len(md_path_split[:-1]) + 1

    else:
        md_dir = os.path.join(*md_path_split[:-1])
        len_dir = len(md_path_split[:-1]) + 1

    md_file_name_list = md_path_split[-1].split('_')
    for i in range(len_dir):
        md_file_name_list.pop(0)

    ol_md_file_name = ('_').join(md_file_name_list)
    # print(os.path.join("repo_docs/docs/docs", md_dir, ol_md_file_name))

    return os.path.join("repo_docs/docs/docs", md_dir, ol_md_file_name)

