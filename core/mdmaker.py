from utils.tools import read_file, write_file
import re
import os
import json

class MDMaker():
    def __init__(self, md_path, repo_path, db=None):
        self.md_path = md_path
        self.add_title = []
        self.status = True
        self.repo_path = repo_path
        self.content = self.read_check_file(self.md_path)


    def read_check_file(self, path):
        if not os.path.exists(path):
            print("WARNING: {} have remove in repo".format(path))
            self.status = False
            return None
        else:
            return read_file(path)


    def remove_image_html(self):
        markdown_image_pattern = re.compile(r'!\[.*?\]\(.*?\)', re.MULTILINE)
        html_image_pattern = re.compile(r'<img\s+[^>]*>', re.MULTILINE)
        html_image_pattern2 = re.compile(r'<Image\s+[^>]*>', re.MULTILINE)
        section_pattern = re.compile(r'</Section>|<Section\s+[^>]*>', re.MULTILINE)
        section_pattern2 = re.compile(r'</TabItem>|<TabItem\s+[^>]*>', re.MULTILINE)
        section_pattern3 = re.compile(r'</Tabs>|<Tabs\s+[^>]*>', re.MULTILINE)
        section_pattern4 = re.compile(r'</DocCardList>|<DocCardList\s+[^>]*>', re.MULTILINE)
        section_pattern5 = re.compile(r'</div>|<div\s+[^>]*>', re.MULTILINE)
        section_pattern6 = re.compile(r'</details>|<details\s+[^>]*>', re.MULTILINE)
        section_pattern7 = re.compile(r'</summary>|<summary\s+[^>]*>', re.MULTILINE)
        section_pattern8 = re.compile(r'<details[\s\S]*?<\/details>', re.DOTALL)
        # section_pattern4 = re.compile(r'<br/>|<DocCardList\s+[^>]*>', re.MULTILINE)

        self.content = markdown_image_pattern.sub('', self.content)
        self.content = html_image_pattern.sub('', self.content)
        self.content = html_image_pattern2.sub('', self.content)
        self.content = section_pattern.sub('', self.content)
        self.content = section_pattern2.sub('', self.content)
        self.content = section_pattern3.sub('', self.content)
        self.content = section_pattern4.sub('', self.content)
        self.content = section_pattern5.sub('', self.content)
        # self.content = section_pattern6.sub('', self.content)
        self.content = section_pattern8.sub('', self.content)
        self.content = re.sub(r'<br/>', '', self.content)
        self.content = re.sub(r'\n{2,}', '\n', self.content)

    def remove_table(self):
        # print("!!!!!!!!!!!!!!!!!")
        self.content = re.sub(r'---{2,}', '', self.content)
        self.content = re.sub(r'─{2,}', '', self.content)
        self.content = re.sub(r'___{2,}', '', self.content)
        self.content = re.sub(r'   {2,}', '', self.content)
        self.content = re.sub(r'│', '', self.content)
        self.content = re.sub(r'\|', '', self.content)
        self.content = re.sub(r'┤', '', self.content)
        self.content = re.sub(r'├', '', self.content)
        self.content = re.sub(r'┐', '', self.content)
        self.content = re.sub(r'┌', '', self.content)
        self.content = re.sub(r'└', '', self.content)
        self.content = re.sub(r'┘', '', self.content)
        self.content = re.sub(r'▒', '', self.content)
        self.content = re.sub(r':{2,}', '', self.content)
        self.content = re.sub(r'\n{2,}', '\n', self.content)


    def recover_link(self):
        link_pattern = re.compile(r'\[\s*([^\]]*)\s*\]\(\s*([^\)]*)\s*\)', re.IGNORECASE)
        links = link_pattern.findall(self.content)
        office_link = "https://docs.radxa.com/"
        over_str = "repo_docs/docs/docs/"
        file_link = self.md_path[len(over_str):-3]
        if file_link.rsplit('/', 1)[-1] == "README":
            file_link = file_link.rsplit('/', 1)[0]
        file_link = office_link + file_link
        # print(file_link)

        for i in links:
            if i[1].startswith("http"):
                continue
            elif i[1].startswith("#"):
                pattern = re.compile(r'^(#+)(.*)', re.MULTILINE)
                matches = pattern.findall(i[1])
                sub_title = matches[0][-1]
                http_link = "{}#{}".format(file_link, sub_title)
                # print(http_link)
            elif i[1].startswith('/'):
                http_link = office_link + i[1][1:]
                # print(http_link)
            else:
                http_link = "{}/../{}".format(file_link, i[1])
                # print(file_link)
                # print(http_link)
            self.content = self.content.replace("[{}]({})".format(i[0], i[1]), "[{}]({})".format(i[0], http_link))


    def get_add_title(self):
        file_path = os.path.normpath(self.md_path)
        # if file_path.startswith(no_need_path):
        #     file_path = file_path[len(no_need_path) + 1:]
        # 判断层级数来确定需要的标题
        title_lists = file_path.split('/')[2:]
        # print(file_path)
        # print(title_lists)
        lever_num = len(title_lists)

        if lever_num > 3:
            product_name = title_lists[2]
            self.add_title.append(product_name)
        elif lever_num <= 2:
            self.add_title.append('')
        else:
            product_name = title_lists[1]
            self.add_title.append(product_name)

        # print(self.add_title)


        level1_pattern = r'^(#\s+)(.*)'
        level1_title = re.search(level1_pattern, self.content, flags=re.MULTILINE)

        if level1_title is not None:
            self.add_title.append(level1_title.group(2))
        else:
            self.add_title.append('')
        # print(self.add_title)

    def import_mdx(self):
        import_pattern = re.compile(r'import\s+(.*)\s+from\s+(.*)', re.MULTILINE)
        imports = import_pattern.findall(self.content)

        if len(imports) != 0:
            for import_name, path in imports:
                mdx_path = path.replace('\\', '')
                mdx_path = mdx_path.replace('\"', '')
                mdx_path = mdx_path.replace('\'', '')
                mdx_path = mdx_path.replace(';', '')
                component_pattern = re.compile(rf'<{import_name}(.*)/>', re.MULTILINE)
                # component_pattern2 = re.compile(rf'</{import_name}>', re.MULTILINE)
                component_use = component_pattern.findall(self.content)
                # component_use2 = component_pattern2.findall(self.content)
                mdx_file_path = os.path.join(os.path.dirname(self.md_path), mdx_path)

                if len(component_use) != 0:
                    if os.path.exists(os.path.normpath(mdx_file_path)):
                        # print("find")
                        mdx_content = read_file(mdx_file_path)
                        # print(f"<{import_name}{component_use[0]}/>")
                        # print(f'import {import_name} from {path}')
                        # if len(component_use) != 0 :
                        self.content = self.content.replace(f'import {import_name} from {path}', '')
                        self.content = self.content.replace(f'<{import_name}{component_use[0]}/>', mdx_content)
                        # print(import_name)
                            # print("{} mdx finish".format(self.md_path))
                        # if component_use2 != 0:
                        #     self.content = self.content.replace(f'import {import_name} from {path}', '')
                        #     self.content = self.content.replace(f'</{import_name}>', mdx_content)

                    else:
                        print(f"Warning: MDX file '{mdx_file_path}' does not exist. in {self.md_path}")

        # print(self.orl_content)
    def remove_sidebar(self):
        side_bar_re = re.compile(r'^---\s*(?:[\s\S]*?)\s*---\s*', re.MULTILINE)
        self.content = side_bar_re.sub('', self.content)
        # print(self.content)

    def insert_title(self, level=5):
        self.get_add_title()

        level1_pattern = r'^(#\s+)(.*)'
        self.content = re.sub(
            level1_pattern,
            lambda m: f'{m.group(1)}{self.add_title[0]} {m.group(2)}',
            self.content,
            flags=re.MULTILINE
        )

        pattern = r'^(#{2,%d}\s+)(.*)' % level
        # 使用正则表达式替换匹配的标题
        self.content = re.sub(
            pattern,
            lambda m: f'{m.group(1)}{self.add_title[0]} {self.add_title[1]} {m.group(2)}',
            self.content,
            flags=re.MULTILINE
        )
        # 输出结果以检查
        # print(self.content)

    def find_table(self):
        table_pattern = re.compile(r'-{10,}', re.MULTILINE)
        wrong_format = re.compile(r'─{10}', re.MULTILINE)
        return bool(table_pattern.search(self.content)) or bool(wrong_format.search(self.content))

    def write_md(self):
        file_splits = self.md_path.split('/')
        # print(file_splits)

        file_name = "_".join(file_splits[3:])

        if os.path.join(*file_splits[:-1]) == self.repo_path:
            dst_path = os.path.join('', file_name)
        else:
            dst_path = os.path.join(*file_splits[3:-1], file_name)
        # print("ZZZ")
        # print(file_name)
        # print(dst_path)

        dst_file_path = os.path.join("./dist/", dst_path)
        dst_dir_path = os.path.join(*dst_file_path.split('/')[:-1])


        if not os.path.exists(dst_dir_path):
            os.makedirs(dst_dir_path, exist_ok=True)

        if self.find_table():
            # print("WARNING: {} with table".format(self.md_path))
            self.remove_table()
            write_file(self.content, dst_file_path)
            return "WARNING", os.path.normpath(dst_file_path)
        else:
            write_file(self.content, dst_file_path)
            return "ACCEPT", os.path.normpath(dst_file_path)




    def forward(self):
        if self.status:
            # print(self.md_path)
            self.remove_sidebar()
            self.import_mdx()
            self.remove_image_html()
            self.insert_title()
            self.recover_link()
            result_log = self.write_md()
            # print(self.content)

            return result_log
        else:
            return "ERROR", self.md_path


