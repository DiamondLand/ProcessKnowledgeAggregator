import os


def find_photo_in_folder(folder_path: str, id: int, user_login: str=None):
    for file_name in os.listdir(folder_path):
        if user_login:
            if file_name.startswith(f"{id}_{user_login}_"):
                return os.path.join(folder_path, file_name)
        else:
            if file_name.startswith(f"{id}_"):
                return os.path.join(folder_path, file_name)
    return None
