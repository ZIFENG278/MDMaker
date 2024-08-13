import os
from core.mdmaker import MDMaker
from core.mdspliter import MdSpliter



class MDExporter():
    def __init__(self, docs_path):
        self.docs_path = docs_path
        self.repo_all_md_path = self.find_md_files(path=self.docs_path)
        self.dist_all_md_path = self.find_md_files(path="./dist")
        self.warning_files_list = {}
    def find_md_files(self, path):
        md_files = []
        for root, dirs, files in os.walk(self.docs_path):
            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
        return md_files

    def mdmaker_loop(self):
        for i in self.repo_all_md_path:
            mdmaker = MDMaker(i, project_path=self.docs_path)
            result_log = mdmaker.forward()
            self.
                self.warning_files_list.append(result_log)

    def mdspliter_loop(self):
        for i in self.warning_files_list:
            print(i)
            print(self.dist_all_md_path[0])
            self.dist_all_md_path.remove(i)
        # for i in self.dist_all_md_path:
        #     mdspliter = MdSpliter(i, 1000, pre_split=True)
        #     mdspliter.forward()




a = MDExporter('/home/zifeng/Job/git_clone/MDMaker/data/docs')
a.mdmaker_loop()
print(len(a.warning_files_list))
a.mdspliter_loop()
print(len(a.warning_files_list))

# for i in a.warning_files_list:
#     print(i)
# a.mdspliter_loop()