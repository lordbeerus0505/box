"""Mapping for command invoke name to logic"""
from .commands import list_all,user_details,create_folder,rename,move_file,file_content,search_item,download_file


commands_by_invoke_name = {

    "list_all":list_all,
    "user_details":user_details,
    "create_folder":create_folder,
    "rename":rename,
    "move_file":move_file,
    "file_content":file_content,
    "search_item":search_item,
    "download_file":download_file,
}