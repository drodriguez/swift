# swift_build_support/products/cmark.py -------------------------*- python -*-
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

from . import product
from .cmake_product_builder import CMakeProductBuilder
from .. import shell


class CMark(product.Product):
    @classmethod
    def make_builder(cls, args, toolchain, workspace, host):
        return CMarkBuilder(args, toolchain, workspace, host)


class CMarkBuilder(CMakeProductBuilder):
    def __init__(self, args, toolchain, workspace, host):
        CMakeProductBuilder.__init__(
            self, CMark, args, toolchain, workspace, host)

        self._cmake_options.define(
            'CMAKE_BUILD_TYPE:STRING', self._build_variant)

        if host.platform.is_darwin:
            cmark_c_flags = self._common_cross_cflags
            if self._is_release_build_variant:
                cmark_c_flags += ' -fno-stack-protector'
            sdk_name = shell.xcrun_show_sdk_path(host.platform.name)
            self._cmake_options.extend([
                ('CMAKE_C_FLAGS', cmark_c_flags),
                ('CMAKE_CXX_FLAGS', cmark_c_flags)
                ('CMAKE_OSX_SYSROOT:PATH', sdk_name)])
            if host.name == 'macosx-x86_64':
                self._cmake_options.define('CMAKE_OSX_DEPLOYMENT_TARGET',
                                           args.darwin_deployment_version_osx)

    @property
    def _build_variant(self):
        return self._args.cmark_build_variant

    @property
    def _test_executable_target(self):
        return 'api_test'

    @property
    def _test_results_targets(self):
        if self._args.cmake_generator == 'Xcode':
            return ['RUN_TESTS']
        else:
            return ['test']
