import os
import subprocess
from utils.build_db import BuildDB
from plugin.kbapi import KbApi
from core.mdexporter import MDExporter
from utils.tools import recover_ol_md_path, get_cur_head
from setting import *

class Updater(BuildDB):
    def __init__(self):
        self.need_delete_set = set()
        self.need_update_set = set()
        self.db = self.read_db()

    def git_pull(self, git_repo_path=repo_docs_path):
        try:
            # Check if the path is a valid Git repository
            if not os.path.isdir(git_repo_path):
                print(f"Error: {git_repo_path} is not a valid directory.")
                return None
            
            # Run git rev-parse HEAD command in the specified directory
            result = subprocess.run(
                ['git', 'pull'],
                cwd=git_repo_path,
                capture_output=True,
                text=True,
                check=True
            )
                
        except subprocess.CalledProcessError as e:
            print(f"Error git pull: {e.stderr.strip()}")
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None


        result_str = result.stdout.strip()
        cur_head = get_cur_head(repo_docs_path)
        if cur_head == self.db["base"]["HEAD"]:
            print("GIT: Already up to date")
            print("No any files need to update")
        else:
            try:
                result = subprocess.run(['git', 'diff', '--name-status', self.db["base"]["HEAD"]], cwd=git_repo_path, capture_output=True, text=True, check=True)

            except subprocess.CalledProcessError as e:
                print(f"Error git pull: {e.stderr.strip()}")
                return None
            
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                return None
        
            result_str = result.stdout.strip()
            print(result_str)
            if len(result_str) > 0:
                result_str_split = result_str.split('\n')
                for i in result_str_split:
                    split_status = i.split()
                    if split_status[1].endswith('.md') and split_status[1].startswith('docs') and split_status[1].split('/')[1] != 'template' and split_status[1].split('/')[-1] != 'Home.md':
                        if split_status[0] == "M": 
                            # 修改 md, 直接重新 导出 dist, 并更新 md， db 是 直接替换，dist 也是直接替换
                            self.need_update_set.add(os.path.join(repo_docs_path, split_status[1]))
                        elif split_status[0] == "A": 
                            #  新增 md, 直接导出 dist
                            self.need_update_set.add(os.path.join(repo_docs_path, split_status[1]))
                        elif split_status[0] == "D":
                            # 删除 需要 删除 db 和 dist 的输出
                            self.need_delete_set.add(os.path.join(repo_docs_path, split_status[1]))
                        elif split_status[0].startswith("R"):
                            # 替代，需要 先删除 db 和 dist 输出 在 重新录入
                            self.need_delete_set.add(os.path.join(repo_docs_path, split_status[1]))
                            self.need_update_set.add(os.path.join(repo_docs_path, split_status[2]))


                    elif split_status[1].endswith('.mdx'):
                        # print(split_status)
                        if split_status[0] == "M":
                            # 如果 mdx 修改，那要找到母 md 进行重新录入 db
                            for key, value in self.db["content"].items():
                                if os.path.join(repo_docs_path, split_status[1]) in value["mdx"]:
                                    self.need_update_set.add(key) ## 这里存在 mdx, 但是已经更换母 md 的情况，需要在数据库中，处理空索引
                        elif split_status[0] == "A":
                            # 一般 ADD mdx 都会伴随 md 的加入，所以不单独处理 mdx 的添加，如果存在单独添加 mdx 的情况，再来调整逻辑
                            pass
                        elif split_status[0] == "D":
                            pass
                            # 如果删除 mdx， 那 md 会修改，被修改，只需要更新 db 即可, 不需要处理

                        elif split_status[0].startswith("R"):
                            pass
                            # 如果 replace mdx. md 会修改，只需更新 db 即可，不需要处理
        return

    def delete_useless(self, enable_api=False):
        print(self.need_delete_set)
        api = KbApi(self.db)
        for i in self.need_delete_set:
            if  i in self.db["content"]:
                if enable_api:
                    api.delete_docs(kb_name="radxa_docs_2", delete_files_path=self.db["content"][i]["split"])

                try:
                    os.remove(self.db["content"][i]["export"])
                    print("delete dist file: {}".format(self.db["content"][i]["export"]))

                except:
                    print("WARNING: delete: {} not exist".format(self.db["content"][i]["export"]))

                for k in self.db["content"][i]["split"]:
                    ol_dir_path = k.split("/")[:-1]
                    ol_file_name = k.split("/")[-1].split("_",1)[-1]
                    # print(os.path.join(*ol_dir_path,ol_file_name))
                    try:
                        os.remove(os.path.join(*ol_dir_path,ol_file_name))
                        break
                    except:
                        print("WARNING: delete: {} not exist".format(os.path.join(*ol_dir_path,ol_file_name)))
                        break
                for j in self.db["content"][i]["split"]:
                    try:
                        os.remove(j)
                    except:
                        print("WARNING: delete: {} not exist".format(j))


                del self.db["content"][i]


    def update(self):
        print(self.need_update_set)
        exporter = MDExporter(docs_list=self.need_update_set, db=self.db)
        exporter.forward(api_delete=False)
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
        self.git_pull(repo_docs_path)
        self.delete_useless()
        self.update()
        # self.api_update()
        # self.db["base"]["HEAD"] = get_cur_head(repo_docs_path)
        self.count_all_split_md()
        # self.show_db()
        self.write_db()
