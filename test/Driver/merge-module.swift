// RUN: %swiftc_driver -emit-module -driver-print-jobs %s 2>&1 > %t.simple.txt
// RUN: %FileCheck --enable-yaml-compatibility %s < %t.simple.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix SIMPLE %s < %t.simple.txt

// RUN: %swiftc_driver -driver-print-jobs -emit-module %s -sdk %S/../Inputs/clang-importer-sdk -Xfrontend -foo -Xfrontend -bar -o sdk.out -emit-objc-header-path path/to/header.h -F /path/to/frameworks -F /path/to/more/frameworks -I /path/to/headers -I path/to/more/headers -module-cache-path /tmp/modules 2>&1 > %t.complex.txt
// RUN: %FileCheck --enable-yaml-compatibility %s < %t.complex.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix COMPLEX %s < %t.complex.txt

// RUN: %swiftc_driver -driver-print-jobs -c -emit-module %s -o sdk.foo.out 2>&1 > %t.complex.txt
// RUN: %FileCheck --enable-yaml-compatibility %s < %t.complex.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix TWO-OUTPUTS %s < %t.complex.txt

// RUN: %swiftc_driver -driver-print-jobs -c %s -emit-objc-header -o sdk.foo.out 2>&1 > %t.complex.txt
// RUN: %FileCheck --enable-yaml-compatibility %s < %t.complex.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix THREE-OUTPUTS %s < %t.complex.txt

// RUN: %swiftc_driver -emit-module -driver-print-jobs -driver-filelist-threshold=0 %s %S/../Inputs/empty.swift -module-name main 2>&1 | %FileCheck --enable-yaml-compatibility -check-prefix FILELISTS %s

// CHECK: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend
// CHECK: -module-name {{[^ ]+}}
// CHECK: -o [[OBJECTFILE:.*]]

// CHECK-NEXT: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend
// CHECK: -emit-module
// CHECK: -module-name {{[^ ]+}}
// CHECK: -o {{[^ ]+}}


// SIMPLE: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend
// SIMPLE: -emit-module
// SIMPLE: -primary-file
// SIMPLE: -emit-module-doc-path {{[^ ]*[/\\]}}merge-module-{{[^ ]*}}.swiftdoc
// SIMPLE: -o {{[^ ]*[/\\]}}merge-module-{{[^ ]*}}.swiftmodule
// SIMPLE: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend
// SIMPLE: -emit-module
// SIMPLE: -o main.swiftmodule


// COMPLEX: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend
// COMPLEX: -emit-module
// COMPLEX-DAG: -emit-module-doc-path {{[^ ]*[/\\]}}merge-module-{{[^ ]*}}.swiftdoc
// COMPLEX-DAG: -sdk {{.*}}/Inputs/clang-importer-sdk
// COMPLEX-DAG: -foo -bar
// COMPLEX-DAG: -F /path/to/frameworks -F /path/to/more/frameworks
// COMPLEX-DAG: -I /path/to/headers -I path/to/more/headers
// COMPLEX-DAG: -module-cache-path /tmp/modules
// COMPLEX: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend
// COMPLEX: -emit-module
// COMPLEX-DAG: -F /path/to/frameworks -F /path/to/more/frameworks
// COMPLEX-DAG: -I /path/to/headers -I path/to/more/headers
// COMPLEX-DAG: -emit-objc-header-path path/to/header.h
// COMPLEX: -o sdk.out


// TWO-OUTPUTS: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend
// TWO-OUTPUTS: -emit-module-path [[MODULE:[^ ]+]]
// TWO-OUTPUTS: -emit-module-doc-path {{[^ ]*[/\\]}}merge-module-{{[^ ]*}}.swiftdoc
// TWO-OUTPUTS: -o {{[^ ]*[/\\]}}merge-module-{{[^ ]*}}.o
// TWO-OUTPUTS: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend
// TWO-OUTPUTS: -emit-module [[MODULE]]
// TWO-OUTPUTS: -o main.swiftmodule

// THREE-OUTPUTS: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend
// THREE-OUTPUTS: -emit-module-path [[MODULE:[^ ]+]]
// THREE-OUTPUTS: -emit-module-doc-path {{[^ ]*[/\\]}}merge-module-{{[^ ]*}}.swiftdoc
// THREE-OUTPUTS: -o {{[^ ]*[/\\]}}merge-module-{{[^ ]*}}.o
// THREE-OUTPUTS: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend
// THREE-OUTPUTS: -emit-module [[MODULE]]
// THREE-OUTPUTS: -emit-objc-header-path sdk.foo.h
// THREE-OUTPUTS: -o sdk.foo.out


// FILELISTS: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend
// FILELISTS-NEXT: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend
// FILELISTS-NEXT: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend
// FILELISTS-NOT: .swiftmodule
// FILELISTS: -filelist {{[^ ]+}}
// FILELISTS-NOT: .swiftmodule
// FILELISTS: -o {{[^ ]+}}


// RUN: %swiftc_driver -driver-print-jobs -emit-module %S/Inputs/main.swift %S/Inputs/lib.swift -module-name merge -o /tmp/modules > %t.complex.txt
// RUN: %FileCheck --enable-yaml-compatibility %s < %t.complex.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix MERGE_1 %s < %t.complex.txt

// MERGE_1: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend -emit-module -primary-file PATH(({{[^ ]+}}/Inputs/main.swift)){{"?}} PATH(({{[^ ]+}}/Inputs/lib.swift))
// MERGE_1: -emit-module-doc-path [[PARTIAL_MODULE_A:[^ ]+]].swiftdoc
// MERGE_1: -module-name merge
// MERGE_1: -o [[PARTIAL_MODULE_A]].swiftmodule
// MERGE_1: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend -emit-module PATH(({{[^ ]+}}/Inputs/main.swift)){{"?}} -primary-file PATH(({{[^ ]+}}/Inputs/lib.swift))
// MERGE_1: -emit-module-doc-path [[PARTIAL_MODULE_B:[^ ]+]].swiftdoc
// MERGE_1: -module-name merge
// MERGE_1: -o [[PARTIAL_MODULE_B]].swiftmodule
// MERGE_1: PATH((bin/swift{{c?(\.exe)?"?}})) -frontend -merge-modules -emit-module [[PARTIAL_MODULE_A]].swiftmodule{{"?}} [[PARTIAL_MODULE_B]].swiftmodule
// MERGE_1: -parse-as-library
// MERGE_1: -emit-module-doc-path {{"?}}PATH((/tmp/modules.swiftdoc)){{"?}}
// MERGE_1: -module-name merge
// MERGE_1: -o /tmp/modules
