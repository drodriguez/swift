# swift_build_support/products/llvm.py --------------------------*- python -*-
#
# This source file is part of the Swift.org open source project
#
# Copyright (c) 2014 - 2017 Apple Inc. and the Swift project authors
# Licensed under Apache License v2.0 with Runtime Library Exception
#
# See https://swift.org/LICENSE.txt for license information
# See https://swift.org/CONTRIBUTORS.txt for the list of Swift project authors
#
# ----------------------------------------------------------------------------

from . import product, cmake_product_builder
from .. import cmake, shell
from ..targets import StdlibDeploymentTarget

import errno
import os
import platform


class LLVM(product.Product):

    @classmethod
    def make_builder(cls, args, toolchain, workspace, host):
        return LLVMBuilder(args, toolchain, workspace, host)

    def __init__(self, args, toolchain, source_dir, build_dir):
        product.Product.__init__(self, args, toolchain, source_dir,
                                 build_dir)

        # Add the cmake option for enabling or disabling assertions.
        self.cmake_options.define(
            'LLVM_ENABLE_ASSERTIONS:BOOL', args.llvm_assertions)

        # Add the cmake option for LLVM_TARGETS_TO_BUILD.
        self.cmake_options.define(
            'LLVM_TARGETS_TO_BUILD', args.llvm_targets_to_build)

        # Add the cmake options for vendors
        self.cmake_options.extend(self._compiler_vendor_flags)

        # Add the cmake options for compiler version information.
        self.cmake_options.extend(self._version_flags)

    @property
    def _compiler_vendor_flags(self):
        if self.args.compiler_vendor == "none":
            return []

        if self.args.compiler_vendor != "apple":
            raise RuntimeError("Unknown compiler vendor?!")

        return [
            ('CLANG_VENDOR', 'Apple'),
            ('CLANG_VENDOR_UTI', 'com.apple.compilers.llvm.clang'),
            # This is safe since we always provide a default.
            ('PACKAGE_VERSION', self.args.clang_user_visible_version)
        ]

    @property
    def _version_flags(self):
        result = cmake.CMakeOptions()
        if self.args.clang_compiler_version is not None:
            result.define(
                'CLANG_REPOSITORY_STRING',
                "clang-{}".format(self.args.clang_compiler_version))
        return result


class LLVMBase(cmake_product_builder.CMakeProductBuilder):
    def __init__(self, product_class, args, toolchain, workspace, host):
        cmake_product_builder.CMakeProductBuilder.__init__(
            self, product_class, args, toolchain, workspace, host)

    @property
    def _is_llvm_lto_enabled(self):
        # TODO: build-script-impl has different arguments for LLVM and Swift,
        # but build-script only has --lto-type
        return self._args.lto_type in ['thin', 'full']

    @property
    def _is_swift_lto_enabled(self):
        # TODO: build-script-impl has different arguments for LLVM and Swift,
        # but build-script only has --lto-type
        return self._args.lto_type in ['thin', 'full']

    @property
    def _cmake_needs_to_specify_standard_computed_defaults(self):
        cmake_version_output = shell.capture(['cmake', '--version'])
        version_lines = [line
                         for line in cmake_version_output.splitlines()
                         if "cmake version" in line]
        if len(version_lines) > 0:
            version_line_fields = version_lines[0].split(" ")
            if len(version_line_fields) >= 3:
                version = version_line_fields[2]
                if version == "3.4.0":
                    return True
        return False

    @property
    def _llvm_cmake_options(self):
        options = cmake.CMakeOptions()

        if self._host.platform.is_darwin:
            cmake_osx_deployment_target = ""
            if self._host.name == 'macosx-x86_64':
                cmake_osx_deployment_target = \
                    self._args.darwin_deployment_version_osx
            options.extend([
                ('CMAKE_OSX_DEPLOYMENT_TARGET:STRING',
                 cmake_osx_deployment_target),
                ('CMAKE_OSX_SYSROOT:PATH',
                 shell.xcrun_show_sdk_path(self._host.platform.name))
                ('COMPILER_RT_ENABLE_IOS', False),
                ('COMPILER_RT_ENABLE_WATCHOS', False),
                ('COMPILER_RT_ENABLE_TVOS', False),
                ('SANITIZER_MIN_OSX_VERSION', cmake_osx_deployment_target),
                ('LLVM_ENABLE_MODULES:BOOL', self._args.llvm_enable_modules)])

            if self._is_llvm_lto_enabled:
                if self._cmake_needs_to_specify_standard_computed_defaults:
                    options.extend([
                        ('CMAKE_C_STANDARD_COMPUTED_DEFAULT', 'AppleClang'),
                        ('CMAKE_CXX_STANDARD_COMPUTED_DEFAULT', 'AppleClang')])

                options.define(
                    'LLVM_PARALLEL_LINK_JOBS',
                    min(self._args.llvm_max_parallel_lto_link_jobs,
                        self._args.build_jobs))

            if self._is_swift_lto_enabled:
                options.define('LLVM_ENABLE_MODULE_DEBUGGING', False)

        # NOTE: compute_cmake_llvm_tool_disable_flags is commented out in
        # build-script-impl

        options.extend([
            ('LLVM_TOOL_COMPILER_RT_BUILD:BOOL', self._args.build_compiler_rt),
            ('LLVM_BUILD_EXTERNAL_COMPILER_RT:BOOL',
             self._args.build_compiler_rt)])

        llvm_target_archs = {
            'linux-armv6': 'ARM',
            'linux-armv7': 'ARM',
            'iphoneos-armv7': 'ARM',
            'iphoneos-armv7s': 'ARM',
            'watchos-armv7k': 'ARM',
            'iphoneos-arm64': 'AArch64',
            'appletvos-arm64': 'AArch64',
            'iphonesimulator-i386': 'X86',
            'iphonesimulator-x86_64': 'X86',
            'appletvsimulator-x86_64': 'X86',
            'watchsimulator-i386': 'X86',
        }

        if self._host.name in llvm_target_archs:
            options.define(
                'LLVM_TARGET_ARCH', llvm_target_archs[self._host.name])

        host_triple = self._swift_host_triple
        if host_triple:
            options.define('LLVM_HOST_TRIPLE:STRING', host_triple)

        if self._args.lit_args:
            options.define('LLVM_LIT_ARGS', self._args.lit_args)

        if self._args.clang_profile_instr_use:
            options.define(
                'CLANG_PROFDATA_FILE', self._args.clang_profile_instr_use)

        options.extend([
            ('CMAKE_INSTALL_PREFIX:PATH', self._host_install_prefix),
            ('INTERNAL_INSTALL_PREFIX', 'local')])

        return options


class LLVMBuilder(LLVMBase):
    def __init__(self, args, toolchain, workspace, host):
        LLVMBase.__init__(
            self, LLVM, args, toolchain, workspace, host)

        self._cmake_options.extend([
            ('CMAKE_LIBTOOL', self._toolchain.libtool),
            ('CMAKE_C_FLAGS_RELWITHDEBINFO', self.__relWithDebInfoCFlags),
            ('CMAKE_CXX_FLAGS_RELWITHDEBINFO', self.__relWithDebInfoCFlags),
            ('CMAKE_BUILD_TYPE:STRING', self._build_variant),
            ('LLVM_TOOL_SWIFT_BUILD', False),
            ('LLVM_INCLUDE_DOCS', True),
            ('LLVM_ENABLE_LTO', self._args.lto_type)])

        clang_tools_extra_source_dir = os.path.join(
            self._source_dir, os.path.pardir, 'clang-tools-extra')
        if os.path.exists(clang_tools_extra_source_dir):
            self._cmake_options.define(
                'LLVM_EXTERNAL_CLANG_TOOLS_EXTRA_SOURCE_DIR',
                clang_tools_extra_source_dir)

        if self._args.build_toolchain_only:
            self._cmake_options.extend([
                ('LLVM_BUILD_TOOLS', False),
                ('LLVM_INSTALL_TOOLCHAIN_ONLY', True),
                ('LLVM_INCLUDE_TESTS', False),
                ('CLANG_INCLUDE_TESTS', False),
                ('LLVM_INCLUDE_UTILS', False),
                ('LLVM_TOOL_LLI_BUILD', False),
                ('LLVM_TOOL_LLVM_AR_BUILD', False),
                ('CLANG_TOOL_CLANG_CHECK_BUILD', False),
                ('CLANG_TOOL_ARCMT_TEST_BUILD', False),
                ('CLANG_TOOL_C_ARCMT_TEST_BUILD', False),
                ('CLANG_TOOL_C_INDEX_TEST_BUILD', False),
                ('CLANG_TOOL_DRIVER_BUILD',
                 not self._args.build_runtime_with_host_compiler),
                ('CLANG_TOOL_DIAGTOOL_BUILD', False),
                ('CLANG_TOOL_SCAN_BUILD_BUILD', False),
                ('CLANG_TOOL_SCAN_VIEW_BUILD', False),
                ('CLANG_TOOL_CLANG_FORMAT_BUILD', False)])

        if not self._args.llvm_include_tests:
            self._cmake_options.extend([
                ('LLVM_INCLUDE_TESTS', False),
                ('CLANG_INCLUDE_TESTS', False)])

        self._cmake_options.extend([
            ('CMAKE_C_FLAGS', self.__cflags),
            ('CMAKE_CXX_FLAGS', self.__cflags)])

        if self._is_cross_tools_host:
            host_llvm = LLVM.make_builder(
                self._args,
                self._toolchain,
                self._workspace,
                StdlibDeploymentTarget.get_target_for_name(
                    self._args.host_target))
            self._cmake_options.extend([
                ('LLVM_TABLEGEN', host_llvm.llvm_tblgen_path),
                ('CLANG_TABLEGEN', host_llvm.clang_tblgen_path),
                ('LLVM_NATIVE_BUILD', host_llvm.build_dir)])

        self._cmake_options += self._llvm_cmake_options

    def do_build(self):
        cmake_invocation = cmake.CMake(self._args, self._toolchain)
        cmake_invocation.generate_if_needed(self._source_dir,
                                            self._build_dir,
                                            self._cmake_options)

        # When we are building LLVM create symlinks to the c++ headers. We need
        # to do this before building LLVM since compiler-rt depends on being
        # built with the just built clang compiler. These are normally put into
        # place during the cmake step of LLVM's build when libcxx is in
        # tree... but we are not building llvm with libcxx in tree when we
        # build swift. So we need to do configure's work here.
        host_cxx_headers_dir = None
        if platform.system() == 'Darwin':
            host_cxx_dir = os.path.dirname(self._toolchain.cxx)
            host_cxx_headers_dir = os.path.join(
                host_cxx_dir, '..', '..', 'usr', 'include', 'c++')
        elif platform.system() == 'Haiku':
            host_cxx_headers_dir = '/boot/system/develop/headers/c++'
        else:  # Linux
            host_cxx_headers_dir = '/usr/include/c++'

        if host_cxx_headers_dir:
            # Find the path in which the local clang build is expecting to find
            # the c++ header files.
            built_cxx_include_dir = os.path.join(
                self._build_dir, 'include', 'c++')

            print(
                "symlinking the system headers ({}) into the local clang "
                "build directory ({})".format(
                    host_cxx_headers_dir, built_cxx_include_dir))
            # This should be equivalent to ln -s -f
            try:
                os.symlink(host_cxx_headers_dir, built_cxx_include_dir)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    os.remove(os.path.join(built_cxx_include_dir))
                    os.symlink(host_cxx_headers_dir, built_cxx_include_dir)
                else:
                    raise e

        if self._should_build:
            cmake_invocation.build_targets(self._build_dir,
                                           self._build_variant,
                                           self._build_targets)

    @property
    def build_dir(self):
        return self._build_dir

    @property
    def tools_path(self):
        return os.path.join(self._build_dir, 'bin')

    @property
    def clang_path(self):
        return os.path.join(self.tools_path, 'clang')

    @property
    def clangpp_path(self):
        return os.path.join(self.tools_path, 'clang++')

    @property
    def llvm_tblgen_path(self):
        return os.path.join(self.tools_path, 'llvm-tblgen')

    @property
    def clang_tblgen_path(self):
        return os.path.join(self.tools_path, 'clang-tblgen')

    @property
    def _build_targets(self):
        build_targets = ['all']
        if self._args.clean_llvm:
            build_targets = ['clean']
        if not self._should_build:
            build_targets = [
                'llvm-tblgen',
                'clang-headers',
                'intrinsics_gen',
                'clang-tablegen-targets']
        return build_targets

    @property
    def _build_variant(self):
        return self._args.llvm_build_variant

    @property
    def _should_build(self):
        return self._args.build_llvm

    @property
    def _should_test(self):
        return False  # We don't test LLVM

    @property
    def __cflags(self):
        cflags = self._common_cross_cflags

        if self._is_release_build_variant:
            cflags += ' -fno-stack-protector'
        if self._is_debinfo_build_variant:
            if self._is_llvm_lto_enabled:
                cflags += ' -gline-tables-only'
            else:
                cflags += ' -g'
        return cflags

    @property
    def __relWithDebInfoCFlags(self):
        return "-O2 -DNDEBUG"
