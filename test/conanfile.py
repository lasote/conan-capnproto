from conans.model.conan_file import ConanFile
from conans import CMake
import os
import subprocess
import signal

############### CONFIGURE THESE VALUES ##################
default_user = "lasote"
default_channel = "testing"
#########################################################

channel = os.getenv("CONAN_CHANNEL", default_channel)
username = os.getenv("CONAN_USERNAME", default_user)

class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"
    requires = "capnproto/0.5.3@%s/%s" % (username, channel)

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake %s %s' % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def imports(self):
        self.copy(pattern="*.dll", dst="", src="bin")
        self.copy(pattern="*.dylib", dst="", src="lib")
        
    def test(self):
        process = subprocess.Popen(
            "cd bin && .%scalculator_server localhost:8888 &" % os.sep, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            shell=True, 
            preexec_fn=os.setsid
        ) 
        
        self.run("cd bin && .%scalculator_client localhost:8888" % os.sep)
        
        os.killpg(process.pid, signal.SIGTERM)
