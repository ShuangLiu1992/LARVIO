from conans import ConanFile, CMake, tools
from conans.tools import os_info, SystemPackageTool
import os


class SLAMConan(ConanFile):
    name = "slam"
    version = "0.0.0"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Hello here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    generators = "cmake"

    requires = ["ceres_solver/2.0.0",
                "eigen/3.4-rc1",
                "boost/1.75.0",
                "glog/0.4.0",
                "gflags/2.2.2",
                "opencv/4.5.2",
                "pangolin/0.6",
                ]

    keep_imports = True

    def system_requirements(self):
        if os_info.linux_distro == "ubuntu":
            installer = SystemPackageTool()
            installer.install("ninja-build")

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib", dst="bin", src="lib")
        self.copy("*", dst="bin", src="bin")

    def configure(self):
        if self.settings.os == "Android":
            self.options["opencv"].shared = False

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=os.environ['VIS_SRC_DIR'])
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["Vis"]

    def generate(self):
        f = open("conan_toolchain.cmake", "w")
        toolchain_file = ""
        if self.settings.os == "Emscripten":
            toolchain_file = self.deps_env_info["emsdk"].CONAN_CMAKE_TOOLCHAIN_FILE
        if self.settings.os == "Android":
            toolchain_file = self.deps_env_info["android-ndk"].CONAN_CMAKE_TOOLCHAIN_FILE
            info = self.deps_env_info['android-ndk']
            f.write(f"set(ANDROID_PLATFORM {info.ANDROID_NATIVE_API_LEVEL})\n")
            f.write(f"set(ANDROID_ABI {info.ANDROID_ABI})\n")
        if self.settings.os in ["Emscripten", "Android"]:
            f.write(f"include({toolchain_file})")
        f.close()
