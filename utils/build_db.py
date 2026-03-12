import json
import os
import re
from utils.tools import get_cur_head, read_file, git_clone
import subprocess
from core.mdexporter import MDExporter
from setting import *

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
                "export": dist_xxx.md
                }
"""

class BuildDB():
    def __init__(self,):
        self.md_num = None
        self.en_md_num = None
        self.repo_all_md_path = None
        self.en_repo_all_md_path = None
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
        if not os.path.exists('./json'):
            os.makedirs('./json', exist_ok=True)
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
            home_path = root[len(path)+1:]
            if home_path == "":
                product_series = None
            else:
                product_series = root.split('/')[0]

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

    # def record_mdx(self, doc_path):
    #     """
    #     给的 doc_path 必须真实存在，务必提前做检查
    #     记录所有 md： md, mdx, split, remote
    #     :param doc_path:
    #     :return:
    #     """
    #     # print(doc_path)
    #     content = read_file(doc_path)
    #     import_pattern = re.compile(r'import\s+(.*)\s+from\s+(.*)', re.MULTILINE)
    #     imports = import_pattern.findall(content)

    #     if doc_path not in self.db["content"]:
    #         # print(doc_path)# 初始化数据
    #         self.db["content"][doc_path] = {
    #             "md": doc_path,
    #             "mdx": [],
    #             "split": {},
    #             # "remote": False
    #         }

    #     if len(imports) != 0:
    #         for import_name, path in imports:
    #             mdx_path = path.replace('\\', '')
    #             mdx_path = mdx_path.replace('\"', '')
    #             mdx_path = mdx_path.replace('\'', '')
    #             mdx_path = mdx_path.replace(';', '')
    #             component_pattern = re.compile(rf'<{import_name}(.*)/>', re.MULTILINE)
    #             component_use = component_pattern.findall(content)
    #             mdx_file_path = os.path.join(os.path.dirname(doc_path), mdx_path)
    #             # print(mdx_file_path)
    #             if len(component_use) != 0:
    #                 if os.path.exists(mdx_file_path):
    #                     self.db["content"][doc_path]["mdx"].append(os.path.normpath(mdx_file_path))



    def count_all_split_md(self):
        count = 0
        for i in self.db["content"]:
            # print(i)
            # print(len(self.db["content"][i]["split"]))
            count += len(self.db["content"][i]["split"])
        self.db["base"]["md_split_number"] = count


    def forward(self, api=True, show_db=False):
        if not os.path.exists(repo_docs_path):
            git_result = git_clone(repo_url=repo_url, dest_dir=repo_docs_path)
            if not git_result:
                print("git clone failed, check the network or repo url")
                return
        self.db["base"]["HEAD"] = get_cur_head(os.path.join(repo_docs_path))

        self.md_num, self.repo_all_md_path = self.find_md_files(path=zh_docs_path)
        self.db["base"]["md_number"] = self.md_num
        # for i in self.repo_all_md_path:
        #     self.record_mdx(i)
        exporter = MDExporter(docs_list=self.repo_all_md_path, db=self.db)
        exporter.forward(api_delete=False, mdsplit=False)

        print("radxa offline zh docs export to ./dist/zh successfully!")

        self.en_md_num, self.en_repo_all_md_path = self.find_md_files(path=en_docs_path)

        self.db["base"]["md_number"] += self.en_md_num
        # for i in self.en_repo_all_md_path:
        #     self.record_mdx(i)
        exporter = MDExporter(docs_list=self.en_repo_all_md_path, db=self.db)
        exporter.forward(api_delete=False, mdsplit=False)
        print("radxa offline en docs export to ./dist/en successfully!")


        self.count_all_split_md()
        self.write_db()
        # if api:
        #     api = KbApi()
        #     api.forward("radxa_docs", "瑞莎radxa文档知识库", './dist_2') # TODO
        if show_db:
            self.show_db()

