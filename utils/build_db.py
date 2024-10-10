import json
import os
import re
from utils.tools import read_file
import subprocess
from core.mdexporter import MDExporter

"""
DB = {
    "base": {"HEAD": str,
             "md_number": int,
             "md_split_number": int               
            }
    "content": {"xxx.md": {
                "md": xx.md,
                "mdx":[xxx.mdx],
                "split":[0_xxx.md, 1_xxx.md],
                "remote": Bool
                }
"""

class BuildDB():
    def __init__(self, docs_path):
        self.docs_path = os.path.normpath(docs_path) # "./repo_docs/docs"
        self.zh_docs_path = os.path.join(self.docs_path, "docs")
        self.md_num = None
        self.repo_all_md_path = None
        self.db = self.read_db()

    def read_db(self):
        """
        读 database
        :return:
        """
        if not os.path.exists('./json/db.json'):
            print("create new db")
            return {"base": {},
                    "content":{}
                    }
        else:
            print("use exist db")
            with open('./json/db.json', 'r') as f:
                return json.load(f)

    def write_db(self):
        with open('./json/db.json', 'w') as f:
            json.dump(self.db, f, ensure_ascii=False)

    def show_db(self):
        print(json.dumps(self.db, ensure_ascii=False, indent=4))

    def find_md_files(self, path):
        """
        找到所有 md 文件， 除了 common 和 template 还有 Home.md
        :param path:
        :return:
        """
        md_files = []
        for root, dirs, files in os.walk(path):
            if root == self.zh_docs_path:
                product_series = None
            else:
                product_series = root.split('/')[3]

            if product_series == "common" or product_series == "template":
                continue

            for file in files:
                if file == "Home.md":
                    continue
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))

        # print(len(md_files)) # 1224
        # print(md_files[22]) # ./repo_docs/docs/docs/zero/zero/radxa-os/social.md
        return len(md_files), md_files

    def record_mdx(self, doc_path):
        """
        给的 doc_path 必须真实存在，务必提前做检查
        记录所有 md： md, mdx, split, remote
        :param doc_path:
        :return:
        """
        # print(doc_path)
        content = read_file(doc_path)
        import_pattern = re.compile(r'import\s+(.*)\s+from\s+(.*)', re.MULTILINE)
        imports = import_pattern.findall(content)

        if doc_path not in self.db["content"]:
            # print(doc_path)# 初始化数据
            self.db["content"][doc_path] = {
                "md": doc_path,
                "mdx": [],
                "split": {},
                # "remote": False
            }

        if len(imports) != 0:
            for import_name, path in imports:
                mdx_path = path.replace('\\', '')
                mdx_path = mdx_path.replace('\"', '')
                mdx_path = mdx_path.replace('\'', '')
                mdx_path = mdx_path.replace(';', '')
                component_pattern = re.compile(rf'<{import_name}(.*)/>', re.MULTILINE)
                component_use = component_pattern.findall(content)
                mdx_file_path = os.path.join(os.path.dirname(doc_path), mdx_path)
                # print(mdx_file_path)
                if len(component_use) != 0:
                    if os.path.exists(mdx_file_path):
                        self.db["content"][doc_path]["mdx"].append(os.path.normpath(mdx_file_path))

    def get_cur_head(self, git_repo_path):
        original_dir = os.getcwd()
        os.chdir(git_repo_path)
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True)
        os.chdir(original_dir)
        return result.stdout.strip()



    def count_all_split_md(self):
        count = 0
        for i in self.db["content"]:
            # print(i)
            # print(len(self.db["content"][i]["split"]))
            count += len(self.db["content"][i]["split"])
        self.db["base"]["md_split_number"] = count


    def forward(self, api=True, show_db=False):
        self.db["base"]["HEAD"] = self.get_cur_head(self.docs_path)
        self.md_num, self.repo_all_md_path = self.find_md_files(path=self.zh_docs_path)
        self.db["base"]["md_number"] = self.md_num
        for i in self.repo_all_md_path:
            self.record_mdx(i)
        # self.show_db()
        exporter = MDExporter(docs_path=self.docs_path, db=self.db)
        exporter.forward(api_delete=False)
        self.count_all_split_md()
        self.write_db()
        # if api:
        #     api = KbApi()
        #     api.forward("radxa_docs", "瑞莎radxa文档知识库", './dist_2') # TODO
        # if show_db:
        # self.show_db()

