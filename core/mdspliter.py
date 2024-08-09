from utils.tools import read_file
import re

class MdSpliter():
    def __init__(self, file_path, split_number):
        self.md_path = file_path
        self.split_number = split_number
        self.content = read_file(self.md_path)
        self.split_content = []
    def extract_titles(self, sub_md_content):
        """从 Markdown 内容中提取所有标题和其 # 符号"""
        # 正则表达式模式，用于匹配标题和 # 符号
        pattern = re.compile(r'^(#+\s+)(.*)', re.MULTILINE)

        # 查找所有标题
        matches = pattern.findall(sub_md_content)

        # 提取标题中的 # 符号和标题文本
        titles = matches[-1]
        titles_str = "{}{}".format(titles[0], titles[1])
        print(titles_str)
        return titles_str

    def check_length(self, content_list):
        for i in content_list:
            if len(i) > 1000:
                sub_title = self.extract_titles(i)
                len_sub_title = len(sub_title)
                split_num = len(i) // 1000 if len(i) % 1000 == 0 else len(i) // 1000 + 1


    def split(self, content=None):
        if content is None:
            content = self.content
        pattern = re.compile(r'(#+\s+.*?)(?=\n#+\s|$)', re.DOTALL)
        matches = pattern.findall(content)
        # split_content = []
        str_count = 0
        temp_str = ""
        md_mata = {}
        # if len > 1000, split first

        for index, sub_content in enumerate(matches):
            print(index)
            if str_count + len(sub_content) < self.split_number:
                str_count += len(sub_content)
                temp_str += sub_content

            else:
                md_mata["content_len"] = str_count
                md_mata["content"] = temp_str
                print(md_mata)
                self.split_content.append(md_mata)
                print("reset")
                md_mata = {}
                str_count = len(sub_content)
                temp_str = sub_content

            if index == len(matches) - 1:
                print(index)
                if len(temp_str) < self.split_number:
                    md_mata["content_len"] = str_count
                    md_mata["content"] = temp_str
                    self.split_content.append(md_mata)
                    print("add2")

    def recover_title(self,content):
        cur_title = self.extract_titles(content)




