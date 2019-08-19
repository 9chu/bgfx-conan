from   conans       import ConanFile, CMake
from   distutils.dir_util import copy_tree


class BgfxConan(ConanFile):
    name            = "bgfx"
    version         = "20190604.018bbc4"
    description     = "Conan package for bgfx."
    url             = "https://github.com/9chu/bgfx-conan"
    license         = "BSD"
    settings        = "arch", "build_type", "compiler", "os"
    generators      = "cmake"
    options         = {"shared": [True, False]}
    default_options = "shared=False"

    def source(self):
        self.run("git clone https://github.com/JoshuaBrookover/bgfx.cmake")
        copy_tree("bgfx.cmake", ".")
        self.run("git reset --hard 018bbc4")
        self.run("git submodule update --init --recursive --depth=1")

    def build(self):
        cmake          = CMake(self)
        shared_options = "-DBUILD_SHARED_LIBS=ON" if self.options.shared else "-DBUILD_SHARED_LIBS=OFF"
        fixed_options  = "-DBGFX_BUILD_EXAMPLES=OFF"
        tool_options   = "-DBGFX_BUILD_TOOLS=OFF" if self.settings.os == "Emscripten" else ""
        opengl_version = "-DBGFX_OPENGL_VERSION=33"
        self.run("cmake %s %s %s %s %s" % (cmake.command_line, shared_options, fixed_options, tool_options, opengl_version))
        self.run("cmake --build . %s -j8" % cmake.build_config)

    def collect_headers(self, include_folder):
        self.copy("*.h"  , dst="include", src=include_folder)
        self.copy("*.hpp", dst="include", src=include_folder)
        self.copy("*.inl", dst="include", src=include_folder)

    def package(self):
        self.collect_headers("bgfx/include")
        self.collect_headers("bimg/include")
        self.collect_headers("bx/include"  )
        self.copy("*.a"  , dst="lib", keep_path=False)
        self.copy("*.so" , dst="lib", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["bgfxd", "bimgd", "bxd"] if self.settings.build_type == "Debug" else ["bgfx", "bimg", "bx"]
        self.cpp_info.libs.extend(["astc-codec", "astc", "edtaa3", "etc1", "etc2", "iqa", "squish", "nvtt", "pvrtc"])
        if self.settings.os == "Macos":
            self.cpp_info.exelinkflags = ["-framework Cocoa", "-framework QuartzCore", "-framework OpenGL", "-weak_framework Metal"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["GL", "X11", "pthread", "dl"])
