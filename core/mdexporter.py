import os
import shutil
import json
from os.path import split, exists

from core.mdmaker import MDMaker
from core.mdspliter import MdSpliter
from plugin.kbapi import KbApi
from utils.tools import copy_md_files_with_numeric_prefix


class MDExporter():
    def __init__(self, docs_path, docs_list=None, db=None):
        self.docs_path = docs_path
        self.docs_list = docs_list
        self.db = db
        self.repo_all_md_path = self.find_md_files(path=self.docs_path)
        self.dist_all_md_path = self.find_md_files(path="./dist")
        self.status_dict = {"WARNING": [],
                            "ACCEPT": [],
                            "ERROR": []}

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

    def copy_to_dist2(self, api_delete=False):
        update_lists = []
        for md_path, mdx_path_list in self.split_path.items():
            split_docs_path = md_path.split('/')[6:]
            split_docs_path[-1] = split_docs_path[-1].split('_', 1)[-1]
            if api_delete and self.db[os.path.join("docs",*split_docs_path)]["split"] != []:
                for i in self.db[os.path.join("docs",*split_docs_path)]["split"]:
                    os.remove(i)
                api = KbApi()
                api.delete_docs(kb_name="radxa_docs", delete_files_path=self.db[os.path.join("docs",*split_docs_path)]["split"])

            dst_mdx_files = []
            for i in mdx_path_list:
                path_split = i.split('/')
                path_split[path_split.index('dist')] = 'dist_2'
                dst_path = os.path.join("/", *path_split)
                if not os.path.exists(os.path.dirname(dst_path)):
                    os.makedirs(os.path.dirname(dst_path))
                shutil.copy(i, dst_path)
                dst_mdx_files.append(dst_path)
            if self.db is not None:
                self.db[os.path.join("docs",*split_docs_path)]["split"] = dst_mdx_files
                for split in dst_mdx_files:
                    update_lists.append(split)


        return update_lists

    def repo_delete(self, api_delete):
        if api_delete:
            for i in self.status_dict["ERROR"]:
                split_docs_path = i.split('/')[7:]
                # print(split_docs_path)
                exists_split_md = self.db[os.path.join(*split_docs_path)]["split"]
                for j in exists_split_md:
                    os.remove(j)
                api = KbApi()
                api.delete_docs(kb_name="radxa_docs",
                                delete_files_path=self.db[os.path.join(*split_docs_path)]["split"])

                del self.db[os.path.join(*split_docs_path)]

        else:
            pass


    def forward(self, api_delete=False):
        self.mdmaker_loop()
        self.mdspliter_loop()
        update_lists = self.copy_to_dist2(api_delete)
        self.repo_delete(api_delete)

        return update_lists











