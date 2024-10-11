import os
import subprocess
from utils.build_db import BuildDB
from plugin.kbapi import KbApi
from core.mdexporter import MDExporter
from utils.tools import recover_ol_md_path
class Updater(BuildDB):
    def __init__(self, docs_path):
        super().__init__(docs_path)
        self.need_delete_set = set()
        self.need_update_set = set()

    def git_pull(self, git_repo_path='./data_test/docs'):
        original_dir = os.getcwd()
        os.chdir(git_repo_path)
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True, check=True)
        result_str = result.stdout.strip()
        # print(result_str)
        os.chdir(original_dir)
        cur_head = self.get_cur_head(self.docs_path)
        if cur_head == self.db["base"]["HEAD"]:
            print("ZZF: Already up to date")
        else:
            os.chdir(git_repo_path)
            result = subprocess.run(['git', 'diff', '--name-status', self.db["base"]["HEAD"]], capture_output=True, text=True, check=True)
            result_str = result.stdout.strip()
            print(result_str)
            if len(result_str) > 0:
                result_str_split = result_str.split('\n')
                for i in result_str_split:
                    split_status = i.split()
                    if split_status[1].endswith('.md') and split_status[1].startswith('docs') and split_status[1].split('/')[1] != 'template' and split_status[1].split('/')[-1] != 'Home.md':
                        if split_status[0] == "M": # md M 重新 恢复一次 mdx，
                            self.need_update_set.add(split_status[1])
                        elif split_status[0] == "A": # 插入 mdx,
                            self.need_update_set.add(split_status[1])
                        elif split_status[0] == "D":
                            self.need_delete_set.add(split_status[1])
                        elif split_status[0].startswith("R"):
                            self.need_delete_set.add(split_status[1])
                            if split_status[2].startswith("i18n"):
                                # print("WARNING: This is the bug of git")
                                over_len = len("i18n/en/docusaurus-plugin-content-docs/current")
                                zh_docs_path = "docs" + split_status[2][over_len:]
                                # print(zh_docs_path)
                                self.need_update_set.add(zh_docs_path)
                                # self.need_delete_set.add(split_status[1])
                            else:
                                self.need_update_set.add(split_status[2])


                    elif split_status[1].endswith('.mdx'):
                        # print(split_status)
                        if split_status[0] == "M":
                            for key, value in self.db["content"].items():
                                if key == "HEAD":
                                    continue
                                if os.path.join(self.docs_path, split_status[1]) in value["mdx"]:
                                    zh_docs_path = os.path.join(*key.split("/")[2:])
                                    self.need_update_set.add(zh_docs_path) ## 这里存在 mdx, 但是已经更换母 md 的情况，需要在数据库中，处理空索引
                        ## 暂时不考虑 D 情况，无耦合
            os.chdir(original_dir)
        return

    def delete_useless(self):
        api = KbApi(self.db)
        for i in self.need_delete_set:
            # print(i)
            md_path = os.path.join(self.docs_path ,i)
            if  md_path in self.db["content"]:
                api.delete_docs(kb_name="radxa_docs_2", delete_files_path=self.db["content"][md_path]["split"])
                for k in self.db["content"][md_path]["split"]:
                    ol_dir_path = k.split("/")[:-1]
                    ol_file_name = k.split("/")[-1].split("_",1)[-1]
                    # print(os.path.join(*ol_dir_path,ol_file_name))
                    try:
                        os.remove(os.path.join(*ol_dir_path,ol_file_name))
                        break
                    except:
                        print("WARNING: delete: {} not exist".format(os.path.join(*ol_dir_path,ol_file_name)))
                        break
                for j in self.db["content"][md_path]["split"]:
                    try:
                        os.remove(j)
                    except:
                        print("WARNING: delete: {} not exist".format(j))


                del self.db["content"][md_path]


    def update(self):
        need_update_full_path = []
        for i in self.need_update_set:
            repo_md_path = os.path.join(self.docs_path, i)
            if os.path.exists(repo_md_path):
                self.record_mdx(repo_md_path)
                need_update_full_path.append(repo_md_path)
            else:
                print("WARNING: {} do not exist, please go confirm".format(repo_md_path))

        print(len(need_update_full_path))
        exporter = MDExporter(docs_path=self.docs_path, docs_list=need_update_full_path, db=self.db)
        update_lists = exporter.forward(api_delete=True)
        # api = KbApi()
        # api.api_upload_files("radxa_docs", update_lists) # TODO

    def init_remote_kb(self):
        api = KbApi(db=self.db)
        upload_file_list = []

        for i in self.db["content"]:
            for j in self.db["content"][i]["split"]:
                upload_file_list.append(j)
        # print(len(upload_file_list))
        api.forward("radxa_docs_2", "瑞莎 radxa 文档知识库", upload_file_list)

        self.write_db()

    def api_update(self):
        api = KbApi(db=self.db)
        upload_file_list = []
        for i in self.db["content"]:
            for md_split_name, remote_status in self.db["content"][i]["split"].items():
                if not remote_status:
                    # print(md_split_name, remote_status)
                    upload_file_list.append(md_split_name)
        api.api_upload_files(kb_name="radxa_docs_2", upload_files_path=upload_file_list)


    def forward(self):
        self.git_pull(self.docs_path)
        self.delete_useless()
        self.update()
        self.api_update()
        self.db["base"]["HEAD"] = self.get_cur_head(self.docs_path)
        self.count_all_split_md()
        # self.show_db()
        self.write_db()
