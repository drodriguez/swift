// RUN: %empty-directory(%t)

// RUN: %swiftc_driver -driver-print-jobs -target x86_64-apple-macosx10.9 %s 2>&1 > %t.simple.txt
// RUN: %FileCheck --enable-yaml-compatibility %s < %t.simple.txt

// RUN: %swiftc_driver -driver-print-jobs -target x86_64-apple-macosx10.9 %s -sdk %S/../Inputs/clang-importer-sdk -Xfrontend -foo -Xfrontend -bar -Xllvm -baz -Xcc -garply -F /path/to/frameworks -Fsystem /path/to/systemframeworks -F /path/to/more/frameworks -I /path/to/headers -I path/to/more/headers -module-cache-path /tmp/modules -incremental 2>&1 > %t.complex.txt
// RUN: %FileCheck %s < %t.complex.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix COMPLEX %s < %t.complex.txt

// RUN: %swiftc_driver -driver-print-jobs -dump-ast -target x86_64-apple-macosx10.9 %s 2>&1 > %t.ast.txt
// RUN: %FileCheck %s < %t.ast.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix AST-STDOUT %s < %t.ast.txt

// RUN: %swiftc_driver -driver-print-jobs -dump-ast -target x86_64-apple-macosx10.9 %s -o output.ast > %t.ast.txt
// RUN: %FileCheck %s < %t.ast.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix AST-O %s < %t.ast.txt

// RUN: %swiftc_driver -driver-print-jobs -emit-silgen -target x86_64-apple-macosx10.9 %s 2>&1 > %t.silgen.txt
// RUN: %FileCheck %s < %t.silgen.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix SILGEN %s < %t.silgen.txt

// RUN: %swiftc_driver -driver-print-jobs -emit-sil -target x86_64-apple-macosx10.9 %s 2>&1 > %t.sil.txt
// RUN: %FileCheck %s < %t.sil.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix SIL %s < %t.sil.txt

// RUN: %swiftc_driver -driver-print-jobs -emit-ir -target x86_64-apple-macosx10.9 %s 2>&1 > %t.ir.txt
// RUN: %FileCheck %s < %t.ir.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix IR %s < %t.ir.txt

// RUN: %swiftc_driver -driver-print-jobs -emit-bc -target x86_64-apple-macosx10.9 %s 2>&1 > %t.bc.txt
// RUN: %FileCheck %s < %t.bc.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix BC %s < %t.bc.txt

// RUN: %swiftc_driver -driver-print-jobs -S -target x86_64-apple-macosx10.9 %s 2>&1 > %t.s.txt
// RUN: %FileCheck %s < %t.s.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix ASM %s < %t.s.txt

// RUN: %swiftc_driver -driver-print-jobs -c -target x86_64-apple-macosx10.9 %s 2>&1 > %t.c.txt
// RUN: %FileCheck %s < %t.c.txt
// RUN: %FileCheck --enable-yaml-compatibility -check-prefix OBJ %s < %t.c.txt

// RUN: not %swiftc_driver -driver-print-jobs -c -target x86_64-apple-macosx10.9 %s %s 2>&1 | %FileCheck --enable-yaml-compatibility -check-prefix DUPLICATE-NAME %s
// RUN: cp %s %t
// RUN: not %swiftc_driver -driver-print-jobs -c -target x86_64-apple-macosx10.9 %s %t/driver-compile.swift 2>&1 | %FileCheck --enable-yaml-compatibility -check-prefix DUPLICATE-NAME %s

// RUN: %swiftc_driver -driver-print-jobs -c -target x86_64-apple-macosx10.9 %s %S/../Inputs/empty.swift -module-name main -driver-filelist-threshold=0 2>&1 | %FileCheck --enable-yaml-compatibility -check-prefix=FILELIST %s

// RUN: %empty-directory(%t)/DISTINCTIVE-PATH/usr/bin/
// RUN: %hardlink-or-copy(from: %swift_driver_plain, to: %t/DISTINCTIVE-PATH/usr/bin/swiftc)
// RUN: ln -s "swiftc" %t/DISTINCTIVE-PATH/usr/bin/swift-update
// RUN: %t/DISTINCTIVE-PATH/usr/bin/swiftc -driver-print-jobs -c -update-code -target x86_64-apple-macosx10.9 %s 2>&1 > %t.upd.txt
// RUN: %FileCheck -check-prefix UPDATE-CODE %s < %t.upd.txt
// Clean up the test executable because hard links are expensive.
// RUN: rm -rf %t/DISTINCTIVE-PATH/usr/bin/swiftc

// RUN: %swiftc_driver -driver-print-jobs -whole-module-optimization -incremental %s 2>&1 > %t.wmo-inc.txt
// RUN: %FileCheck %s < %t.wmo-inc.txt
// RUN: %FileCheck -check-prefix NO-REFERENCE-DEPENDENCIES %s < %t.wmo-inc.txt

// RUN: %swiftc_driver -driver-print-jobs -embed-bitcode -incremental %s 2>&1 > %t.embed-inc.txt
// RUN: %FileCheck %s < %t.embed-inc.txt
// RUN: %FileCheck -check-prefix NO-REFERENCE-DEPENDENCIES %s < %t.embed-inc.txt

// REQUIRES: CODEGENERATOR=X86


// CHECK: PATH((bin/swift))
// CHECK: PATH((Driver/driver-compile.swift))
// CHECK: -o

// COMPLEX: PATH((bin/swift))
// COMPLEX: -c
// COMPLEX: PATH((Driver/driver-compile.swift))
// COMPLEX-DAG: -sdk {{.*}}/Inputs/clang-importer-sdk
// COMPLEX-DAG: -foo -bar
// COMPLEX-DAG: -Xllvm -baz
// COMPLEX-DAG: -Xcc -garply
// COMPLEX-DAG: -F /path/to/frameworks -Fsystem /path/to/systemframeworks -F /path/to/more/frameworks
// COMPLEX-DAG: -I /path/to/headers -I path/to/more/headers
// COMPLEX-DAG: -module-cache-path /tmp/modules
// COMPLEX-DAG: -emit-reference-dependencies-path {{(.*(/|\\))?driver-compile[^ /]+}}.swiftdeps
// COMPLEX: -o {{.+}}.o


// AST-STDOUT: PATH((bin/swift))
// AST-STDOUT: -dump-ast
// AST-STDOUT: -o -

// AST-O: PATH((bin/swift))
// AST-O: -dump-ast
// AST-O: -o output.ast

// SILGEN: PATH((bin/swift))
// SILGEN: -emit-silgen
// SILGEN: -o -

// SIL: PATH((bin/swift))
// SIL: -emit-sil{{ }}
// SIL: -o -

// IR: PATH((bin/swift))
// IR: -emit-ir
// IR: -o -

// BC: PATH((bin/swift))
// BC: -emit-bc
// BC: -o {{[^-]}}

// ASM: PATH((bin/swift))
// ASM: -S{{ }}
// ASM: -o -

// OBJ: PATH((bin/swift))
// OBJ: -c{{ }}
// OBJ: -o {{[^-]}}

// DUPLICATE-NAME: error: filename "driver-compile.swift" used twice: 'PATH(({{.*}}test/Driver/driver-compile.swift))' and '{{.*}}driver-compile.swift'
// DUPLICATE-NAME: note: filenames are used to distinguish private declarations with the same name

// FILELIST: PATH((bin/swift))
// FILELIST: -filelist [[SOURCES:(["][^"]+sources[^"]+["]|[^ ]+sources[^ ]+)]]
// FILELIST: -primary-filelist  {{(["][^"]+primaryInputs[^"]+["]|[^ ]+primaryInputs[^ ]+)}}
// FILELIST: -supplementary-output-file-map {{(["][^"]+supplementaryOutputs[^"]+["]|[^ ]+supplementaryOutputs[^ ]+)}}
// FILELIST: -output-filelist {{[^-]}}
// FILELIST-NEXT: PATH((bin/swift))
// FILELIST: -filelist [[SOURCES]]
// FILELIST: -primary-filelist  {{(["][^"]+primaryInputs[^"]+["]|[^ ]+primaryInputs[^ ]+)}}
// FILELIST: -supplementary-output-file-map {{(["][^"]+supplementaryOutputs[^"]+["]|[^ ]+supplementaryOutputs[^ ]+)}}
// FILELIST: -output-filelist {{[^-]}}

// UPDATE-CODE: PATH(({{DISTINCTIVE-PATH|distinctive-path}}/usr/bin/swift{{c?(\.exe)?}}))
// UPDATE-CODE: -frontend -c
// UPDATE-CODE: -emit-remap-file-path {{.+}}.remap

// NO-REFERENCE-DEPENDENCIES: PATH((bin/swift))
// NO-REFERENCE-DEPENDENCIES-NOT: -emit-reference-dependencies
