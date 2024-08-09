from utils.tools import read_file, write_file
import re
import os

class MDMaker():
    def __init__(self, md_path):
        self.md_path = md_path
        self.orl_content = read_file(self.md_path)
        self.add_title = None
        # self.dst_path
        self.no_need_path = "/home/zifeng/Job/git_clone/docs-template/contents/docs/"
    def remove_image(self):
        markdown_image_pattern = re.compile(r'!\[.*?\]\(.*?\)', re.MULTILINE)
        html_image_pattern = re.compile(r'<img\s+[^>]*>', re.MULTILINE)

        self.orl_content = markdown_image_pattern.sub('', self.orl_content)
        self.orl_content = html_image_pattern.sub('', self.orl_content)

    def get_add_title(self, no_need_path="/home/zifeng/Job/git_clone/docs-template/contents/docs/"):
        file_path = os.path.abspath(self.md_path)
        if file_path.startswith(no_need_path):
            file_path = file_path[len(no_need_path):]

        title_list = file_path.split('/')[:-1]
        self.add_title = " ".join(i for i in title_list)
    def import_mdx(self):
        import_pattern = re.compile(r'import\s+(\w+)\s+from\s+["\'](.*)["\']\s*;', re.MULTILINE)
        # component_pattern = re.compile(r'<(\w+)\s*/>', re.MULTILINE)

        imports = import_pattern.findall(self.orl_content)
        # print(imports)
        if len(imports) != 0:
            for import_name, path in imports:
                mdx_path = path.replace('\\', '')
                mdx_file_path = os.path.join(os.path.dirname(self.md_path), mdx_path)
                if os.path.exists(mdx_file_path):
                    mdx_content = read_file(mdx_file_path)

                    self.orl_content = self.orl_content.replace(f'import {import_name} from \'{path}\';', '')
                    self.orl_content = self.orl_content.replace(f'<{import_name} />', mdx_content)
                else:
                    print(f"Warning: MDX file '{mdx_file_path}' does not exist.")
        # print(self.orl_content)
    def remove_sidebar(self):
        side_bar_re = re.compile(r'^---\s*(?:[\s\S]*?)\s*---\s*', re.MULTILINE)
        self.orl_content = side_bar_re.sub('', self.orl_content)
        # print(self.orl_content)

    def insert_title(self, level=4):
        self.get_add_title()
        pattern = r'^(#{1,%d}\s+)(.*)' % level
        # 使用正则表达式替换匹配的标题
        self.orl_content = re.sub(
            pattern,
            lambda m: f'{m.group(1)}{self.add_title} {m.group(2)}',
            self.orl_content,
            flags=re.MULTILINE
        )
        # 输出结果以检查
        # print(self.orl_content)

    def write_md(self):
        file_path = os.path.abspath(self.md_path)
        file_path = file_path[len(self.no_need_path):]

        dir_name = file_path.rsplit('/', 1)[0]
        file_name = file_path.rsplit('/', 1)[-1]
        dst_dir_path = os.path.join("./dist/", dir_name)
        print(file_name)
        print(dst_dir_path)
        if not os.path.exists(dst_dir_path):
            os.makedirs(dst_dir_path, exist_ok=True)
        write_file(self.orl_content, os.path.join(dst_dir_path, file_name))

    def forward(self):
        self.remove_sidebar()
        self.import_mdx()
        self.insert_title()
        self.remove_image()
        self.write_md()



a = MDMaker('/home/zifeng/Job/git_clone/docs-template/contents/docs/sophon/airbox/casaos/casaos_app_build.md')
a.forward()
# print(a.orl_content)

