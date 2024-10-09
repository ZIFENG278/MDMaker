from utils.tools import read_file, write_file
import re
import os

class MdSpliter():
    def __init__(self, file_path, split_number, repo_path, pre_split=False):
        self.md_path = file_path
        self.repo_path = repo_path
        self.ol_md_path = self.recover_ol_md_path()
        self.split_number = split_number
        self.content = read_file(self.md_path)
        self.split_content = []
        self.pre_split_bool = pre_split

    def recover_ol_md_path(self):
        md_path_split = self.md_path.split('/')[1:]
        # print(md_path_split)
        if len(md_path_split) == 1:
            md_dir = ''
        else:
            md_dir = os.path.join(*md_path_split[:-1])
        ol_md_file_name = md_path_split[-1].split('_', 1)[-1]
        # print(os.path.join("repo_docs/docs/docs", md_dir, ol_md_file_name))
        return os.path.join("repo_docs/docs/docs", md_dir, ol_md_file_name)

    def extract_titles(self, sub_md_content, level=1, status="main"):
        pattern = re.compile(r'^(#{' + str(level) + r',}\s+)(.*)', re.MULTILINE)
        matches = pattern.findall(sub_md_content)
        if len(matches) != 0:
            titles_str = "{}{}\n".format(matches[-1][0], matches[-1][1])
            for i in range(len(matches) -1, -1, -1):
                if matches[i][0] != "#":
                    titles = matches[i]
                    titles_str = "{}{}\n".format(titles[0], titles[1])
                    break
                else:
                    continue
            # print(titles_str)

            return titles_str

        else:

            return None


    def pre_split(self, content_list):
        pre_content = []
        for i in content_list:
            if len(i) > 1000:

                sub_title = self.extract_titles(i, level=1)

                CONTENT_LENGTH = 960
                split_num = len(i) // CONTENT_LENGTH if len(i) % CONTENT_LENGTH == 0 else len(i) // CONTENT_LENGTH + 1
                for j in range(split_num):
                    chunk = i[j*CONTENT_LENGTH: j*CONTENT_LENGTH + CONTENT_LENGTH] + "\n"
                    temp_sub_title = self.extract_titles(chunk, level=2, status="chunk")

                    if temp_sub_title is not None:
                        pass
                    elif temp_sub_title is None:
                        chunk = sub_title + chunk

                    pre_content.append(chunk)
            else:
                pre_content.append(i+"\n")
        return pre_content


    def split(self, content=None):
        if content is None:
            content = self.content
        pattern = re.compile(r'(#+\s+.*?)(?=\n##+\s|$)', re.DOTALL)
        matches = pattern.findall(content)

        matches = self.pre_split(matches)
        # split_content = []
        str_count = 0
        temp_str = ""
        md_mata = {}

        for index, sub_content in enumerate(matches):
            if str_count + len(sub_content) < self.split_number:
                str_count += len(sub_content)
                temp_str += sub_content

            else:
                md_mata["content_len"] = str_count
                md_mata["content"] = temp_str
                self.split_content.append(md_mata)
                md_mata = {}
                str_count = len(sub_content)
                temp_str = sub_content

            if index == len(matches) - 1:
                if len(temp_str) < self.split_number:
                    md_mata["content_len"] = str_count
                    md_mata["content"] = temp_str
                    self.split_content.append(md_mata)

    def write_split_md(self):
        write_file_path = []
        for index, content in enumerate(self.split_content):
            file_dir, md_name = self.md_path.rsplit('/', 1)
            md_name = "{}_{}".format(index, md_name)

            write_file(content["content"], os.path.join(file_dir, md_name))
            # print(os.path.normpath(os.path.join(file_dir, md_name)))
            write_file_path.append(os.path.normpath(os.path.join(file_dir, md_name)))

        return write_file_path
    def forward(self):
        self.split()
        split_path = self.write_split_md()
        # print(self.ol_md_path)
        return split_path, self.ol_md_path










