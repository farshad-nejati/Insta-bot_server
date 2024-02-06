from instagrapi import Client
from datetime import datetime
import os
    
class InstagramUploader:

    def __init__(self, dir_path, credential_file):
        self.dir_path = dir_path
        self.credential_file = credential_file
        self.cl = Client()

    def login_and_get_account_info(self):
        credentioal_path = os.path.join(self.dir_path, self.credential_file)
        
        # with open(f"{self.dir_path}/{self.credential_file}", "r") as f:
        with open(credentioal_path, "r") as f:
            phone, password, username = f.read().splitlines()

        print(f"phone: {phone}")
        print(f"username: {username}")
        
        self.cl.login(phone, password)
        return self.cl.account_info()

    def upload_image_to_instagram(self, caption, file_prefix):
        current_date = datetime.now().strftime("%Y%m%d")
        # image_path = f"{self.dir_path}/generated/output_image_{current_date}.jpg"
        image_path = os.path.join(self.dir_path, f"generated/{file_prefix}_{current_date}.jpg")
        uploaded_media = self.cl.photo_upload(image_path, caption)
        return uploaded_media.dict()
    
