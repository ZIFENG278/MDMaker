
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