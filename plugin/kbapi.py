import requests
import os

class KbApi():
    def __init__(self, upload_files_path):
        self.headers = {"accept": "application/json"}
        self.upload_files_path = upload_files_path
    def api_upload_fiile(self, kb_name):
        if isinstance(self.upload_files_path, str):
            dist2_dir = os.listdir(self.upload_files_path)
            product_list = []
            for i in dist2_dir:
                if os.path.isdir(os.path.join('./dist_2', i)):
                    product_list.append(i)
                else:
                    self.upload_docs(kb_name, os.path.join(self.upload_files_path, i))

            for i in product_list:
                files_list = os.listdir(os.path.join('./dist_2', i))
                for file in files_list:
                    self.upload_docs(kb_name, os.path.join('./dist_2', i, file))


        elif isinstance(self.upload_files_path, list):
            for i in self.upload_files_path:
                file_path = os.path.abspath(i)
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

        response = requests.get(url, headers=self.headers, data=data)

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


    def upload_docs(self, kb_name, file_path, chunk_size="1000"):
        file_path_split = file_path.rsplit('/', 1)
        file_name = file_path_split[-1]

        url = "http://localhost:7861/knowledge_base/upload_docs"
        data = {
            "to_vector_store": "true",
            "override": "true",
            "not_refresh_vs_cache": "false",
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

        response = requests.get(url, headers=self.headers, data=data)

        if response.status_code == 200:
            data = response.json()
            # print(data)
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.json())

    def forward(self, kb_name, kb_info, embedding_model="bge-large-zh-v1.5", vector_store_type="faiss"):
        response = self.create_knowledge_base(kb_name, kb_info, embedding_model, vector_store_type)
        # if response.status_code != 200:
        #     print(response.json())
        #     return
        # self.api_upload_fiile(kb_name)




