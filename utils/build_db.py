import json
import os
import re
from utils.tools import read_file
DB = {}
"""
DB = {
    "HEAD": xxx
    "xxx.md": [xxx.mdx, xxx.mdx]
}
"""


class BuildDB():
    def __init__(self, docs_path):
        self.docs_path = docs_path
        self.repo_all_md_path = self.find_md_files(path=self.docs_path)
        self.db = self.read_db()

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
        return md_files

    def record_mdx(self, doc_path):
        content = read_file(doc_path)
        import_pattern = re.compile(r'import\s+(.*)\s+from\s+(.*)', re.MULTILINE)
        imports = import_pattern.findall(content)
        # print(self.content)
        # print(imports)
        # print("??")
        # print(len(imports))
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
                    # if os.path.exists(mdx_file_path):
                    #
                    #     mdx_path_name = ""
                    #     for i in mdx_path_split:
                    #         if i == "..":
                    #             continue
                    #         if i.endswith('.mdx'):
                    #             mdx_path_name += i
                    #         else:
                    #             mdx_path_name += (i+'/')
                    #
                    #     self.db[doc_path[len(self.docs_path)+1:]] = mdx_path_name



    def forward(self):
        for i in self.repo_all_md_path:
            self.record_mdx(i)

        self.show_db()
