from conans import ConanFile, ConfigureEnvironment
import os
from conans.tools import download, unzip, replace_in_file
from conans import CMake


class CapNProtoConan(ConanFile):
    name = "capnproto"
    version = "0.5.3"
    ZIP_FOLDER_NAME = "capnproto-c++-%s" % version
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    exports = ["CMakeLists.txt"]
    url="http://github.com/lasote/conan-capnproto"
    license="MIT https://github.com/sandstorm-io/capnproto/blob/v0.5.3/LICENSE"

    def config(self):
        del self.settings.compiler.libcxx
        if self.settings.os == "Windows":
            try:
                self.options.remove("fPIC")
            except: 
                pass
        
    def source(self):
        zip_name = "capnproto-c++-%s.tar.gz" % self.version
        download("https://capnproto.org/%s" % zip_name, zip_name)
        unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
            if self.options.fPIC:
                env_line = env.command_line.replace('CFLAGS="', 'CFLAGS="-fPIC ')
            else:
                env_line = env.command_line
            
            if self.settings.os == "Macos":
                old_str = '-install_name \$rpath/\$soname'
                new_str = '-install_name \$soname'
                replace_in_file("./%s/configure" % self.ZIP_FOLDER_NAME, old_str, new_str)
            
            self.output.warn(env_line)
            self.run("cd %s && %s ./configure" % (self.ZIP_FOLDER_NAME, env_line))
            self.run("cd %s && %s make -j6 check" % (self.ZIP_FOLDER_NAME, env_line))

        else:
            cmake = CMake(self.settings)
            if self.settings.os == "Windows":
                self.run("IF not exist _build mkdir _build")
            else:
                self.run("mkdir _build")
            cd_build = "cd _build"
            cmake_1 = '%s && cmake .. %s  -DCAPNP_LITE=1 -DEXTERNAL_CAPNP=1' % (cd_build, cmake.command_line)
            self.output.warn(cmake_1)
            self.run(cmake_1)
            cmake_2 = "%s && cmake --build . %s" % (cd_build, cmake.build_config)
            self.output.warn(cmake_2)
            self.run(cmake_2)

    def package(self):
        """ Define your conan structure: headers, libs, bins and data. After building your
            project, this method is called to create a defined structure:
        """
      
        self.copy(pattern="*.h", dst="include/capnp", src="%s/src/capnp" % self.ZIP_FOLDER_NAME,  keep_path=True)
        self.copy(pattern="*.h", dst="include/kj", src="%s/src/kj" % self.ZIP_FOLDER_NAME,  keep_path=True)


        # Copying static and dynamic libs
        if self.settings.os == "Windows":
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", src="_build", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src="_build", keep_path=False)
        else:
            self.copy(pattern="*/capnp", dst="bin", keep_path=False)
            self.copy(pattern="*/capnpc-c++", dst="bin", keep_path=False)
            self.copy(pattern="*/capnpc-capnp", dst="bin", keep_path=False)
            
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                else:
                    self.copy(pattern="*.so*", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", src="%s/_build" % self.ZIP_FOLDER_NAME, keep_path=False)
                self.copy(pattern="*.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['capnpc', 'capnp-rpc', 'capnp', 'kj-async', 'kj']
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

