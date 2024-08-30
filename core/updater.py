import os
import subprocess
from utils.build_db import BuildDB
from plugin.kbapi import KbApi
from core.mdexporter import MDExporter

class Updater(BuildDB):
    def __init__(self, docs_path):
        super().__init__(docs_path)

    def git_pull(self, git_repo_path='./data_test/docs'):
        original_dir = os.getcwd()
        os.chdir(git_repo_path)
        subprocess.run(['git', 'pull'], capture_output=True, text=True, check=True)
        os.chdir(original_dir)
        cur_head = self.get_cur_head()
        if cur_head == self.db["HEAD"]:
            print("ZZF: Already up to date")
        else:
            os.chdir(git_repo_path)
            result = subprocess.run(['git', 'diff', '--name-only', self.db["HEAD"]], capture_output=True, text=True, check=True)
            result_str = result.stdout.strip()
            if len(result_str) > 0:
                result_str_split = result_str.split('\n')
                for i in result_str_split:
                    if i.endswith('.md') and i.startswith('docs') and i.split('/')[1] != 'template' and  i.split('/')[-1] != 'Home.md':
                        self.need_update_set.add(i)
                        if i not in self.db.keys():
                            self.record_mdx(os.path.join(self.docs_path[:-4], i))
                        self.need_update_set.add(i)
                    elif i.endswith('.mdx'):
                        for key, value in self.db.items():
                            if i in value:
                                self.need_update_set.add(key)
            os.chdir(original_dir)
        return

    def update(self):
        need_update_full_path = []
        print(self.need_update_set)
        for i in self.need_update_set:
            need_update_full_path.append(os.path.join(self.docs_path[:-4], i))
        exporter = MDExporter(docs_path=self.docs_path, docs_list=need_update_full_path, db=self.db)
        update_lists = exporter.forward(api_delete=True)
        api = KbApi()
        api.api_upload_files("radxa_docs", update_lists) # TODO

    def forward(self):
        self.git_pull()
        self.update()
        self.write_db()
