import requests
import os

class KbApi():
    def __init__(self,):
        self.headers = {"accept": "application/json"}


    def api_upload_files(self, kb_name, upload_files_path):
        if isinstance(upload_files_path, str):
            count = 0
            for root, dirs, files in os.walk(upload_files_path):
                for file in files:
                    if file.endswith('.md'):
                            md_file = os.path.join(root, file)
                            self.upload_docs(kb_name, md_file)
                            count += 1
            print("upload {} files".format(count))

        elif isinstance(upload_files_path, list):
            for i in upload_files_path:
                file_path = os.path.normpath(i)
                self.upload_docs(kb_name, file_path)

    def create_knowledge_base(self, kb_name, kb_info=None, embedding_model="bge-large-zh-v1.5", vector_store_type="faiss"):
        url = "http://localhost:7861/knowledge_base/create_knowledge_base"
        data = {
            "knowledge_base_name": kb_name,
            "vector_store_type": vector_store_type,
            "kb_info": kb_info,
            "embed_model": embedding_model

        }

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 200:
            data = response.json()
            # print(data)
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.json())

        return response

    def delete_knowledge_base(self, kb_name):
        url = "http://localhost:7861/knowledge_base/delete_knowledge_base"

        data = kb_name

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 200:
            data = response.json()
            # print(data)
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.json())

    def list_knowledge_bases(self):
        url = "http://localhost:7861/knowledge_base/list_knowledge_bases"

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            for i in data['data']:
                print(i)
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.json())

    def list_knowledge_base_files(self, base_name):
        url = "http://localhost:7861/knowledge_base/list_files?knowledge_base_name={}".format(base_name)

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            print(len(data['data']))
            return len(data['data'])
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.json())

    def upload_docs(self, kb_name, file_path, chunk_size="1000"):
        file_path_split = file_path.rsplit('/', 1)
        file_name = file_path_split[-1]

        url = "http://localhost:7861/knowledge_base/upload_docs"
        data = {
            "to_vector_store": "true",
            "override": "true",
            "not_refresh_vs_cache": "true",
            "chunk_size": chunk_size,
            "chunk_overlap": "150",
            "zh_title_enhance": "false",
            "knowledge_base_name": kb_name
        }

        files = {
            "files": (file_name, open(file_path, "rb"), "text/markdown"),
        }


        # 发送POST请求
        response = requests.post(url, headers=self.headers, data=data, files=files)

        if response.status_code == 200:
            data = response.json()
            # print(data)
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.json())



    def update_info(self, kb_info, kb_name):
        url = "http://localhost:7861/knowledge_base/update_info"
        data = {
            "knowledge_base_name": kb_name,
            "kb_info": kb_info,
        }

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 200:
            data = response.json()
            # print(data)
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.json())

    def delete_docs(self, kb_name, delete_files_path):
        url = "http://localhost:7861/knowledge_base/delete_docs"

        delete_docs_list = []
        for i in delete_files_path:
            file_name = i.rsplit('/', 1)[-1]
            delete_docs_list.append(str(file_name))

        data = {
            "knowledge_base_name": kb_name,
            "file_names": delete_docs_list,
            "delete_content": "true",
            "not_refresh_vs_cache": "true"
        }

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 200:
            data = response.json()
            # print(data)
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.json())  # 打印详细错误信息

    def forward(self, kb_name, kb_info, upload_files_path, embedding_model="bge-base-zh-v1.5", vector_store_type="faiss"):
        response = self.create_knowledge_base(kb_name, kb_info, embedding_model, vector_store_type)
        if response.status_code != 200:
            print(response.json())
            return
        self.update_info(kb_name, kb_info)
        self.api_upload_files(kb_name, upload_files_path)


    def test_api(self):
        self.create_knowledge_base("test_api", "test1", )
        self.list_knowledge_bases()
        self.update_info("test2", "test_api")
        self.upload_docs("test_api", "/home/zifeng/Job/git_clone/MDMaker/dist/zero/zero/radxa-os/1_zero_usbnet.md")
        self.delete_knowledge_base("test_api")




