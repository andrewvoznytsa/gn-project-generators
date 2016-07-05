try:
    from enum import Enum
except ImportError:
    from enum34 import Enum

import posixpath
import os

class TargetType(Enum):
    unknown = 0
    group = 1
    executable = 2
    loadable_module = 3
    shared_library = 4
    static_library = 5
    source_set = 6
    copy_files = 7
    action = 8
    action_foreach = 9
    bundle_data = 10
    create_bundle = 11

class Target:
    def __init__(self, name, json_data, project):

        self.project = project

        self.sources = json_data.get("sources", [])
        self.inputs = json_data.get("inputs", [])
        self.arflags = json_data.get("arflags", [])
        self.asmflags = json_data.get("amflags", [])        
        self.cflags = json_data.get("cflags", [])
        self.cflags_c = json_data.get("cflags_c", [])
        self.cflags_cc = json_data.get("cflags_cc", [])
        self.cflags_objc = json_data.get("cflags_objc", [])
        self.cflags_objcc = json_data.get("cflags_objcc", [])
        self.defines = json_data.get("defines", [])
        self.include_dirs = json_data.get("include_dirs", [])
        self.ldflags = json_data.get("ldflags", [])
        self.lib_dirs = json_data.get("lib_dirs", [])
        self.libs = json_data.get("libs", [])
        self.deps = json_data.get("deps", [])
        self.precompiled_header = json_data.get("precompiled_header", None)
        self.precompiled_source = json_data.get("precompiled_source", None)
        self.output_dir = json_data.get("output_dir", None)
        self.output_name = json_data.get("output_name", None)        
        self.output_extension = json_data.get("output_extension", None)
        self.bundle_data = json_data.get("bundle_data", None)
        self.type = TargetType[json_data["type"].lower()]
        self.toolchain = json_data["toolchain"]        
        self.name = name

    def get_output_name(self):

        basename = self.output_name
        if basename is None: # extract name from target
            basename = posixpath.basename(self.name)
            sep = basename.rfind(":")
            if sep != -1:
                basename = basename[sep+1:]
        
        if self.output_extension is not None:
            basename = os.path.splitext(basename)[0]
            if self.output_extension != "":
                basename += "." + self.output_extension            

        return basename

    def get_output_dir(self):
        
        res = self.output_dir
        if res is None:
            res = self.project.build_dir

        return res

class Project:
    def __init__(self, json_data):
        build_settings = json_data["build_settings"]
        self.root_path = build_settings["root_path"]
        self.build_dir = build_settings["build_dir"]
        self.default_toolchain = build_settings["default_toolchain"]

        self.targets = {}
        for key, value in json_data["targets"].items():
            self.targets[key] = Target(key, value, self)
    
    # Converts project path relative to build folder
    
    def get_relative_path(self, path):          
        if path.startswith("//"): # project relative            
            return posixpath.relpath(self.get_absolute_path(path),
                                     self.get_absolute_build_path())
        else:
            return path # absolute, just return the path

    def get_absolute_build_path(self):
        return self.root_path + "/" + self.build_dir[2:]

    def get_absolute_path(self, path):
        if path.startswith("//"): # project relative
            return self.root_path + "/" + path[2:]
        else:
            return path # absolute    

def overwrite_file_if_different(path, new_content):
    overwrite = True

    if (os.path.exists(path)):
        with open(path) as existing_file:
            exiting_content = existing_file.read()
            if exiting_content == new_content:
                overwrite = False
            existing_file.close()

    if overwrite:
        f = open(path, "w")
        f.write(new_content)            
        f.close()
        return True
    else:
        return False
