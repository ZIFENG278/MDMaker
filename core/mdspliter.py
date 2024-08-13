from utils.tools import read_file, write_file
import re
import os
class MdSpliter():
    def __init__(self, file_path, split_number, pre_split=False):
        self.md_path = file_path
        self.split_number = split_number
        self.content = read_file(self.md_path)
        self.split_content = []
        self.pre_split_bool = pre_split
    def extract_titles(self, sub_md_content):
        pattern = re.compile(r'^(#+\s+)(.*)', re.MULTILINE)
        matches = pattern.findall(sub_md_content)
        if len(matches) != 0:
            titles = matches[-1]
            titles_str = "{}{}\n".format(titles[0], titles[1])
            return titles_str
        else:
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
                sub_title = self.extract_titles(i)
                # len_sub_title = len(sub_title)
                split_num = len(i) // 900 if len(i) % 900 == 0 else len(i) // 900 + 1
                for j in range(split_num):
                    chunk = i[j*900: j*900 + 900]
                    temp_sub_title = self.extract_titles(chunk)
                    if temp_sub_title is not None and j != 0:
                        pass
                    elif temp_sub_title is None:
                        chunk = sub_title + chunk
                        # sub_title = temp_sub_title
                    # if j != 0 and temp_sub_title is not None:
                    #     chunk = sub_title + chunk
                    pre_content.append(chunk)
            else:
                pre_content.append(i)

        return pre_content


    def split(self, content=None):
        if content is None:
            content = self.content
        pattern = re.compile(r'(#+\s+.*?)(?=\n#+\s|$)', re.DOTALL)
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
        for index, content in enumerate(self.split_content):
            file_dir, md_name = self.md_path.rsplit('/', 1)
            md_name = "{}_{}".format(index, md_name)
            # print(file_dir)
            # print(md_name)
            write_file(content["content"], os.path.join(file_dir, md_name))

    def forward(self):
        self.split()
        self.write_split_md()








