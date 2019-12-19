// Emit the explicit module.
// RUN: %empty-directory(%t)
// RUN: %target-swift-emit-pcm -module-name script -o %t/script.pcm %S/Inputs/custom-modules/module.map

// Verify some of the output of the -dump-pcm flag.
// RUN: %swift-dump-pcm %t/script.pcm | %FileCheck %s --check-prefix=CHECK-DUMP
// CHECK-DUMP: Information for module file '{{.*}}/script.pcm':
// CHECK-DUMP:   Module name: script
// CHECK-DUMP:   Module map file: PATH(({{.*}}/Inputs/custom-modules/module.map))

// Compile a source file that imports the explicit module.
// RUN: %target-swift-frontend -typecheck -verify -Xcc -fmodule-file=%t/script.pcm %s

import script
var _ : ScriptTy
