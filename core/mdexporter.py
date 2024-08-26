import os
import shutil

from core.mdmaker import MDMaker
from core.mdspliter import MdSpliter
from utils.tools import copy_md_files_with_numeric_prefix


class MDExporter():
    def __init__(self, docs_path):
        self.docs_path = docs_path
        self.repo_all_md_path = self.find_md_files(path=self.docs_path)
        self.dist_all_md_path = self.find_md_files(path="./dist")
        self.status_dict = {"WARNING": [],
                            "ACCEPT": []}
    def find_md_files(self, path):
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
            mdspliter = MdSpliter(i, 1000, pre_split=True)
            mdspliter.forward()
        for i in self.status_dict["WARNING"]:
            # print("WARNING:table {}".format(i))
            mdspliter = MdSpliter(i, 1000, pre_split=True)
            mdspliter.forward()


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

    def forward(self):
        self.mdmaker_loop()
        self.mdspliter_loop()
        self.copy_dist()









