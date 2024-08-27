from utils.tools import read_file, write_file
import re
import os
import json

class MdSpliter():
    def __init__(self, file_path, split_number, pre_split=False):
        self.md_path = file_path
        self.split_number = split_number
        self.content = read_file(self.md_path)
        self.split_content = []
        self.pre_split_bool = pre_split

    def extract_titles(self, sub_md_content, level=1, status="main"):
        # pattern = re.compile(r'^(##+\s+)(.*)', re.MULTILINE)
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
        # elif len(matches) > 1:
        #     first_titles = matches[0]
        #     last
        else:
            # if level == 1:
            #     print("================================")
            #     print(sub_md_content)
            #     print(level)
            # print("================================")
            # print(self.md_path)
            # print(status)
            return None
    # def code_split(self, code_content):
    #     code_block_pattern = re.compile(r'```[\s\S]*?```', re.DOTALL)
    #     matches = code_block_pattern.findall(code_content)
    #     if len()
    #
    #     code_block_pattern = re.compile(r'```[\s\S]*?```', re.DOTALL)


    def pre_split(self, content_list):
        pre_content = []
        for i in content_list:
            if len(i) > 1000:
                # print(i)
                # print("=======================================================")
                # print(i)
                sub_title = self.extract_titles(i, level=1)
                # print(sub_title)
                # print(i)
                # print()
                # len_sub_title = len(sub_title)
                CONTENT_LENGTH = 960
                split_num = len(i) // CONTENT_LENGTH if len(i) % CONTENT_LENGTH == 0 else len(i) // CONTENT_LENGTH + 1
                for j in range(split_num):
                    chunk = i[j*CONTENT_LENGTH: j*CONTENT_LENGTH + CONTENT_LENGTH] + "\n"
                    temp_sub_title = self.extract_titles(chunk, level=2, status="chunk")
                    # print("========")
                    # print(temp_sub_title)
                    # print("=========")
                    if temp_sub_title is not None:
                        pass
                    elif temp_sub_title is None:
                        chunk = sub_title + chunk
                        # sub_title = temp_sub_title
                    # if j != 0 and temp_sub_title is not None:
                    #     chunk = sub_title + chunk

                    pre_content.append(chunk)
            else:
                pre_content.append(i+"\n")
        # print(pre_content)
        return pre_content


    def split(self, content=None):
        if content is None:
            content = self.content
        pattern = re.compile(r'(#+\s+.*?)(?=\n##+\s|$)', re.DOTALL)
        matches = pattern.findall(content)
        #
        # for i in matches:
        #     print(i)
        #     print("=======================================================")
        #
        # return
        matches = self.pre_split(matches)
        # split_content = []
        str_count = 0
        temp_str = ""
        md_mata = {}
        # if len > 1000, split first

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
            # print(file_dir)
            # print(md_name)
            write_file(content["content"], os.path.join(file_dir, md_name))
            write_file_path.append(os.path.abspath(os.path.join(file_dir, md_name)))

        return write_file_path
    def forward(self):
        self.split()
        split_path = self.write_split_md()

        return split_path










