# swift_build_support/products/builder_host_install_mixin.py ----*- python -*-
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

import os


class BuilderHostInstallMixin(object):
    def __init__(self, args, host):
        self.__args = args
        self.__host = host

    @property
    def _host_install_destdir(self):
        if self.__has_cross_compile_hosts:
            # If cross compiling tools, install into a host-specific
            # subdirectory.
            if self.__should_include_host_in_lipo:
                # If this is one of the hosts we should lipo, install into a
                # temporary subdirectory.
                host_install_destdir = os.path.join(self.__args.build_dir,
                                                    'intermediate-install',
                                                    self.__host.name)
            else:
                host_install_destdir = os.path.join(
                    self.__args.install_destdir, self.__host.name)
        else:
            host_install_destdir = self.__args.install_destdir

        # Should always end in a path separator; it's a directory.
        return os.path.join(host_install_destdir, '')

    @property
    def _host_install_prefix(self):
        if self._is_cross_tools_host and \
                len(self.__args.cross_compile_install_prefixes) > 0:
            try:
                host_index = \
                    self.__args.cross_compile_hosts.index(self.__host.name)
            except ValueError:
                host_index = None
            if host_index is not None and host_index < \
                    len(self.__args.cross_compile_install_prefixes):
                host_install_prefix = \
                    self.__args.cross_compile_install_prefixes[host_index]
            else:
                # If there is no explicit install prefix for this host, use the
                # last one in the list.
                host_install_prefix = \
                    self.__args.cross_compile_install_prefixes[-1]
        else:
            host_install_prefix = self.__args.install_prefix

        # Should always be an absolute path; otherwise CMake will expand it as
        # a relative path from the build folder.
        if not os.path.isabs(host_install_prefix):
            host_install_prefix = os.path.join(os.path.sep,
                                               host_install_prefix)

        # Should always end in a path separator; it's a directory.
        return os.path.join(host_install_prefix, '')

    @property
    def _is_cross_tools_host(self):
        return self.__host.name in self.__args.cross_compile_hosts

    @property
    def _should_skip_local_host_install(self):
        return self.__args.skip_local_host_install and \
            self.__has_cross_compile_hosts and \
            self.__host.name == self.__args.host_target

    @property
    def __has_cross_compile_hosts(self):
        return len(self.__args.cross_compile_hosts) > 0

    @property
    def __should_include_host_in_lipo(self):
        # When building cross-compilers for these hosts, merge all of their
        # contents together with lipo
        return self.__has_cross_compile_hosts and \
            not self.__args.skip_merge_lipo_cross_compile_tools and \
            self.__host.platform.name in ['iphoneos', 'iphonesimulator',
                                          'appletvos', 'appletvsimulator'
                                          'watchos', 'watchossimulator']
