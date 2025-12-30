import requests
import os

class ILovePDFClient:
    def __init__(self, public_key, secret_key):
        self.public_key = public_key
        self.secret_key = secret_key
        self.base_url = 'https://api.ilovepdf.com/v1'
        self.token = None
        self.server = None
        
    def get_token(self):
        url = f'{self.base_url}/auth'
        payload = {'public_key': self.public_key}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            self.token = result.get('token')
            return self.token
        except Exception as e:
            print(f"Auth error: {e}")
            return None

    def start_task(self, tool):
        if not self.token and not self.get_token(): return None
        url = f'{self.base_url}/start/{tool}'
        headers = {'Authorization': f'Bearer {self.token}'}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            self.server = result.get('server')
            return result.get('task')
        except Exception as e:
            print(f"Start task error: {e}")
            return None

    def upload_file(self, task_id, file_path):
        url = f'https://{self.server}/v1/upload'
        headers = {'Authorization': f'Bearer {self.token}'}
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                data = {'task': task_id}
                response = requests.post(url, headers=headers, files=files, data=data)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Upload error: {e}")
            return None

    def process_task(self, task_id, tool, files_data, params=None):
        url = f'https://{self.server}/v1/process'
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        payload = {'task': task_id, 'tool': tool, 'files': files_data}
        if params: payload.update(params)
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Process error: {e}")
            return None

    def download_file(self, task_id, output_path):
        url = f'https://{self.server}/v1/download/{task_id}'
        headers = {'Authorization': f'Bearer {self.token}'}
        try:
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk)
            return True
        except Exception as e:
            print(f"Download error: {e}")
            return False