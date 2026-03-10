import os
import shutil
import re
import glob
import subprocess

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


def git_clone(repo_url="https://github.com/radxa-docs/docs", dest_dir="./radxa-docs"):
    """
    Clone a Git repository to the specified directory.
    
    Args:
        repo_url (str): The URL of the Git repository to clone.
        dest_dir (str): The directory where the repository will be cloned.
    
    Returns:
        bool: True if cloning was successful, False otherwise.
    """
    try:
        # Ensure the destination directory exists
        os.makedirs(dest_dir, exist_ok=True)
        
        # Run git clone command
        result = subprocess.run(
            ['git', 'clone', repo_url, dest_dir],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"Successfully cloned {repo_url} to {dest_dir}")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e.stderr.strip()}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False


def get_cur_head(git_repo_path):
    """
    Get the current HEAD commit hash of a Git repository.
    
    Args:
        git_repo_path (str): The path to the Git repository.
    
    Returns:
        str: The current HEAD commit hash, or None if an error occurs.
    """
    try:
        # Check if the path is a valid Git repository
        if not os.path.isdir(git_repo_path):
            print(f"Error: {git_repo_path} is not a valid directory.")
            return None
        
        # Run git rev-parse HEAD command in the specified directory
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=git_repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        return result.stdout.strip()
    
    except subprocess.CalledProcessError as e:
        print(f"Error getting HEAD commit: {e.stderr.strip()}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None