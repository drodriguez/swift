# swift_build_support/products/cmake_product_builder.py ---------*- python -*-
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

from .product_builder import ProductBuilder
from .builder_host_install_mixin import BuilderHostInstallMixin
from .. import cmake
from ..targets import StdlibDeploymentTarget

import abc


class CMakeProductBuilder(ProductBuilder, BuilderHostInstallMixin):
    def __init__(self, product_class, args, toolchain, workspace, host):
        BuilderHostInstallMixin.__init__(self, args, host)
        self._source_dir = workspace.source_dir(
            product_class.product_source_name())
        self._build_dir = workspace.build_dir(host.name,
                                              product_class.product_name())
        self._product = product_class(
            args, toolchain, self._source_dir, self._build_dir)
        self._args = args
        self._host = host
        self._toolchain = toolchain
        self._workspace = workspace
        self._cmake_options = cmake.CMakeOptions(self._product.cmake_options)

        if self._is_cross_tools_host:
            if self._args.cross_compile_with_host_tools:
                # NOTE: cannot be imported before, because LLVM depends on this
                from .llvm import LLVM
                # Optionally use the freshly-built host copy of clang to build
                # for foreign hosts.
                llvm_build = LLVM.make_builder(
                    self._args,
                    self._toolchain,
                    self._workspace,
                    StdlibDeploymentTarget.get_target_for_name(
                        self._args.host_target))
                toolchain.cc = llvm_build.clang_path
                toolchain.cxx = llvm_build.clangpp_path
            # CMake can't relink when using Ninja, but that's okay -
            # we don't need a build-local rpath because we can't run
            # cross-compiled products
            if self._args.cmake_generator == 'Ninja':
                self._cmake_options.define('CMAKE_BUILD_WITH_INSTALL_RPATH', 1)

    def do_build(self):
        cmake_invocation = cmake.CMake(self._args, self._toolchain)
        cmake_invocation.generate_if_needed(self._source_dir,
                                            self._build_dir,
                                            self._cmake_options)
        if self._should_build:
            cmake_invocation.build_targets(self._build_dir,
                                           self._build_variant,
                                           self._build_targets)

    def do_test(self, force_regenerate=False):
        if self._should_test:
            product_name = self._product.name
            host_name = self._host.name
            cmake_invocation = cmake.CMake(self._args, self._toolchain)
            if force_regenerate:
                cmake_invocation.generate(
                    self._source_dir, self._build_dir, self._cmake_options)
            if self._test_executable_target:
                print("--- Building tests for {} ---".format(product_name))
                cmake_invocation.build_targets(self._build_dir,
                                               self._build_variant,
                                               [self._test_executable_target])
            if self._is_cross_tools_host:
                print("--- Can't execute tests for {}, skipping... ---".format(
                    host_name))
                return
            print("--- Running tests for {} ---".format(product_name))
            for target in self._test_results_targets:
                print("--- {} ---".format(target))
                cmake_invocation.build_targets(self._build_dir,
                                               self._build_variant,
                                               [target])
                print("-- {} finished --".format(target))
            print("--- Finished tests for {} ---".format(product_name))

    def do_install(self):
        if self._should_install:
            host_install_destdir = self._host_install_destdir
            install_targets = ["install"]
            print('--- Installing {} ---'.format(self._product.name))
            cmake_invocation = cmake.CMake(self._args, self._toolchain)
            cmake_invocation.install_targets(self._build_dir,
                                             install_targets,
                                             {'DESTDIR': host_install_destdir})

    @property
    def _build_targets(self):
        return ['all']

    @abc.abstractproperty
    @property
    def _build_variant(self):
        pass

    @property
    def _common_cross_cflags(self):
        cflags = ['-Wno-unknown-warning-option',
                  '-Werror=unguarded-availability-new']

        host_cflags = {
            'iphonesimulator-i386': [
                '-arch i386',
                '-mios-simulator-version-min={}'.format(
                    self._args.darwin_deployment_version_ios)],
            'iphonesimulator-x86_64': [
                '-arch x86_64',
                '-mios-simulator-version-min={}'.format(
                    self._args.darwin_deployment_version_ios)],
            'iphoneos-armv7': [
                '-arch armv7',
                '-miphoneos-version-min={}'.format(
                    self._args.darwin_deployment_version_ios)],
            'iphoneos-armv7s': [
                '-arch armv7s',
                '-miphoneos-version-min={}'.format(
                    self._args.darwin_deployment_version_ios)],
            'iphoneos-arm64': [
                '-arch arm64',
                '-miphoneos-version-min={}'.format(
                    self._args.darwin_deployment_version_ios)],
            'appletvsimulator-x86_64': [
                '-arch x86_64',
                '-mtvos-simulator-version-min={}'.format(
                    self._args.darwin_deployment_version_tvos)],
            'appletvos-arm64': [
                '-arch arm64',
                '-mtvos-version-min={}'.format(
                    self._args.darwin_deployment_version_tvos)],
            'watchsimulator-i386': [
                '-arch i386',
                '-mwatchos-simulator-version-min={}'.format(
                    self._args.darwin_deployment_version_watchos)],
            'watchos-armv7k': [
                '-arch armv7k',
                '-mwatchos-version-min={}'.format(
                    self._args.darwin_deployment_version_watchos)],
            'android-armv7': ['-arch armv7'],
            'android-arm64': ['-arch aarch64'],
        }

        if self._host.name in host_cflags:
            cflags.extend(host_cflags[self._host.name])

        return ' '.join(cflags)

    @property
    def _is_debinfo_build_variant(self):
        return self._build_variant in ['Debug', 'RelWithDebInfo']

    @property
    def _is_release_build_variant(self):
        return self._build_variant in ['Release', 'RelWithDebInfo']

    @property
    def _should_build(self):
        return not self._args.skip_build

    @property
    def _should_test(self):
        return self._args.test

    @property
    def _should_install(self):
        return False and self._should_skip_local_host_install

    @property
    def _swift_host_triple(self):
        # For cross-compilable host, we need to know the triple
        # and it must be the same for both LLVM and Swift
        swift_host_triples = {
            'linux-armv6': 'armv6-unknown-linux-gnueabihf',
            'linux-armv7': 'armv7-unknown-linux-gnueabihf',
            'macosx-x86_64':
                'x86_64-apple-macos{}'.format(
                    self._args.darwin_deployment_version_osx),
            'iphonesimulator-i386':
                'i386-apple-ios{}'.format(
                    self._args.darwin_deployment_version_ios),
            'iphonesimulator-x86_64':
                'x86_64-apple-ios{}'.format(
                    self._args.darwin_deployment_version_ios),
            'iphoneos-armv7':
                'armv7-apple-ios{}'.format(
                    self._args.darwin_deployment_version_ios),
            'iphoneos-armv7s':
                'armv7s-apple-ios{}'.format(
                    self._args.darwin_deployment_version_ios),
            'iphoneos-arm64':
                'arm64-apple-ios{}'.format(
                    self._args.darwin_deployment_version_ios),
            'appletvsimulator-x86_64':
                'x86_64-apple-tvos{}'.format(
                    self._args.darwin_deployment_version_tvos),
            'appletvos-arm64':
                'arm64-apple-tvos{}'.format(
                    self._args.darwin_deployment_version_tvos),
            'watchsimulator-i386':
                'i386-apple-watchos{}'.format(
                    self._args.darwin_deployment_version_watchos),
            'watchos-armv7k':
                'armv7k-apple-watchos{}'.format(
                    self._args.darwin_deployment_version_watchos),
        }

        if self._host.name in swift_host_triples:
            return swift_host_triples[self._host.name]
        else:
            return None

    @property
    def _test_executable_target(self):
        return None

    @property
    def _test_results_targets(self):
        return []
