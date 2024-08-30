import json
import os
import re
from utils.tools import read_file
import subprocess
from core.mdexporter import MDExporter
from plugin.kbapi import KbApi
# DB = {}
"""
DB = {
    "HEAD": xxx
    "xxx.md": [{md: xx.md,
                mdx:[xxx.mdx],
                split:[0_xxx.md, 1_xxx.md]},
                {}]
}
"""

class BuildDB():
    def __init__(self, docs_path):
        self.docs_path = os.path.abspath(docs_path)
        self.repo_all_md_path = self.find_md_files(path=self.docs_path)
        self.db = self.read_db()
        self.need_update_set = set()

    def read_db(self):
        if not os.path.exists('./json/db.json'):
            return {}
        else:
            with open('./json/db.json', 'r') as f:
                return json.load(f)

    def write_db(self):
        with open('./json/db.json', 'w') as f:
            json.dump(self.db, f, ensure_ascii=False)

    def show_db(self):
        print(json.dumps(self.db, ensure_ascii=False, indent=4))

    def find_md_files(self, path):
        md_files = []
        for root, dirs, files in os.walk(self.docs_path):
            # print(root)
            # print(root[len(self.docs_path):])
            dir_name = root[len(self.docs_path) + 1:].split('/')[0]
            if  dir_name == "common" or dir_name == "template":
                continue
            for file in files:
                if file == "Home.md":
                    continue
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
        # print(md_files)
        return md_files

    def record_mdx(self, doc_path):
        content = read_file(doc_path)
        import_pattern = re.compile(r'import\s+(.*)\s+from\s+(.*)', re.MULTILINE)
        imports = import_pattern.findall(content)
        # print(self.content)
        # print(imports)
        # print("??")
        # print(len(imports))

        if "docs/" + doc_path[len(self.docs_path) + 1:] not in self.db.keys():
            self.db["docs/" + doc_path[len(self.docs_path) + 1:]] = {
                "md": "docs/" + doc_path[len(self.docs_path) + 1:]}
            self.db["docs/" + doc_path[len(self.docs_path) + 1:]]["mdx"] = []
            self.db["docs/" + doc_path[len(self.docs_path) + 1:]]["split"] = []

        if len(imports) != 0:
            for import_name, path in imports:
                mdx_path = path.replace('\\', '')
                mdx_path = mdx_path.replace('\"', '')
                mdx_path = mdx_path.replace('\'', '')
                mdx_path = mdx_path.replace(';', '')
                component_pattern = re.compile(rf'<{import_name}(.*)/>', re.MULTILINE)
                component_use = component_pattern.findall(content)
                mdx_file_path = os.path.join(os.path.dirname(doc_path), mdx_path)
                if len(component_use) != 0:
                    if os.path.exists(mdx_file_path):
                        self.db["docs/" + doc_path[len(self.docs_path) + 1: ]]["mdx"].append("docs/" + os.path.abspath(mdx_file_path)[len(self.docs_path)+1:])

    def get_cur_head(self, git_repo_path='./data_test/docs'):
        original_dir = os.getcwd()
        os.chdir(git_repo_path)
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True)
        # print(result.stdout.strip())
        os.chdir(original_dir)
        return result.stdout.strip()


    def forward(self):
        self.db["HEAD"] = self.get_cur_head()
        for i in self.repo_all_md_path:
            self.record_mdx(i)
        exporter = MDExporter(docs_path=self.docs_path, db=self.db)
        exporter.forward(api_delete=False)
        self.write_db()
        api = KbApi()
        api.forward("radxa_docs", "瑞莎radxa文档知识库", './dist_2') # TODO
        self.show_db()

