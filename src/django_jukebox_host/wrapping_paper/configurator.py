import tomllib
import pathlib
from pathlib import Path
import sys
from django.core.management.utils import get_random_secret_key

class configurator():
    def get_metadata_file(self):
        return Path(__file__).resolve().parent.parent / "pyproject.toml"
    
    def __init__(self, touch_files = True):
        if pathlib.Path.exists(self.get_metadata_file()):
            data = tomllib.load(open(self.get_metadata_file(), 'rb')).get('tool').get('poetry')
            self.name = data.get('name')
            self.version = data.get('version')
            self.dot_directory = pathlib.Path.home() / ".{}".format(self.name)
            if Path.exists(self.dot_directory):
                pass
            else:
                pathlib.Path.mkdir(self.dot_directory)
                pathlib.Path.touch(self.dot_directory / "settings.py")
                open(self.dot_directory / "settings.py", 'w').writelines([
                    "SECRET_KEY='{}'\n".format(str(self.get_random_secret_key()))])
        else:
            raise Exception("error loading package metadata {}".format(self.get_metadata_file()))
    
    def get_version(self):
        if self.version == None:
            raise Exception("error loading package metadata")
        return self.version

    def get_name(self):
        if self.name == None:
            raise Exception("error loading package metadata")
        return self.name
    
    def get_dot_directory(self):
       if self.dot_directory == None or not pathlib.Path.exists(self.dot_directory):
            raise Exception("error loading package metadata")
       return self.dot_directory
    
    def get_random_secret_key(self):
        return get_random_secret_key()

    def create_dir_if_not_exists(self, check_path: Path, mode = 511):
        if check_path.exists():
            return check_path
        else:
            print("creating directory {}".format(check_path))
            check_path.mkdir(parents = True, mode = mode)
    