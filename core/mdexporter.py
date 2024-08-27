import os
import shutil
import json
from core.mdmaker import MDMaker
from core.mdspliter import MdSpliter
from utils.tools import copy_md_files_with_numeric_prefix


class MDExporter():
    def __init__(self, docs_path, docs_list=None, db=None):
        self.docs_path = docs_path
        self.docs_list = docs_list
        self.db = db
        self.repo_all_md_path = self.find_md_files(path=self.docs_path)
        self.dist_all_md_path = self.find_md_files(path="./dist")
        self.status_dict = {"WARNING": [],
                            "ACCEPT": []}

        self.split_path = {}


    def find_md_files(self,path):
        if self.docs_list is not None:
            return self.docs_list
        else:
            md_files = []
            for root, dirs, files in os.walk(self.docs_path):
                dir_name = root[len(self.docs_path) + 1:].split('/')[0]
                if  dir_name == "common" or dir_name == "template":
                    continue
                for file in files:
                    if file == "Home.md":
                        continue
                    if file.endswith('.md'):
                        md_files.append(os.path.join(root, file))
            return md_files

    def mdmaker_loop(self):
        for i in self.repo_all_md_path:
            mdmaker = MDMaker(i, project_path=self.docs_path)
            result_status, result_log = mdmaker.forward()
            self.status_dict[result_status].append(result_log)

    def mdspliter_loop(self):
        for i in self.status_dict["ACCEPT"]:
            # print(self.docs_path)
            # print(i)
            mdspliter = MdSpliter(i, 1000, pre_split=True)
            split_path = mdspliter.forward()
            self.split_path[i] = split_path

        for i in self.status_dict["WARNING"]:
            # print("WARNING:table {}".format(i))
            mdspliter = MdSpliter(i, 1000, pre_split=True)
            split_path = mdspliter.forward()
            self.split_path[i] = split_path


    def copy_dist(self):
        dist_dir = os.listdir('./dist')
        product_list = []
        for i in dist_dir:
            if os.path.isdir(os.path.join('./dist', i)):
                product_list.append(i)
            else:
                src_file = os.path.join('./dist', i)
                dest_file = os.path.join('./dist_2', i)
                shutil.copy(src_file, dest_file)

        for i in product_list:
            copy_md_files_with_numeric_prefix(os.path.join('./dist', i), os.path.join('./dist_2', i))

    def copy_to_dist2(self):
        dist_2_files = []
        for md_path, mdx_path_list in self.split_path.items():
            dst_mdx_files = []
            for i in mdx_path_list:
                path_split = i.split('/')
                path_split[path_split.index('dist')] = 'dist2'
                dst_path = os.path.join("/", *path_split)
                if not os.path.exists(os.path.dirname(dst_path)):
                    os.makedirs(os.path.dirname(dst_path))
                shutil.copy(i, dst_path)
                dst_mdx_files.append(dst_path)

            split_docs_path = md_path.split('/')[6:]
            split_docs_path[-1] = split_docs_path[-1].split('_', 1)[-1]
            # try:
            self.db[os.path.join("docs",*split_docs_path)]["split"] = dst_mdx_files
            # except Exception as e:
            #     with open('./json/db.json', 'w') as f:
            #         json.dump(self.db, f, ensure_ascii=False)


    def forward(self):
        self.mdmaker_loop()
        self.mdspliter_loop()
        # print(self.split_path)
        self.copy_to_dist2()











