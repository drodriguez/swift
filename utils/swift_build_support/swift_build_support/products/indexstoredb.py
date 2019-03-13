# swift_build_support/products/indexstoredb.py -------------------*- python -*-
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
from .build_script_helper_builder import BuildScriptHelperBuilder


class IndexStoreDB(product.Product):
    @classmethod
    def product_source_name(cls):
        return "indexstore-db"

    @classmethod
    def is_build_script_impl_product(cls):
        return False

    @classmethod
    def make_builder(cls, args, toolchain, workspace, host):
        return IndexStoreDBBuilder(args, toolchain, workspace, host)


class IndexStoreDBBuilder(BuildScriptHelperBuilder):
    def __init__(self, args, toolchain, workspace, host):
        BuildScriptHelperBuilder.__init__(self, IndexStoreDB, args, toolchain,
                                          workspace, host)
        self.__args = args

    def _should_test(self):
        return self.__args.test and self.__args.test_indexstoredb
