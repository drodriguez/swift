// RUN: %swiftc_driver -driver-print-jobs -target x86_64-unknown-linux-gnu -g %s | %FileCheck %s

// CHECK: PATH((bin/swiftc?(\.exe)?"?)) -frontend{{.*}}-emit-module-path [[MOD:.*\.swiftmodule]]
// CHECK: PATH((bin/swiftc?(\.exe)?"?)) {{.*}}-emit-module [[MOD]]
// CHECK-SAME:                                 -o [[MERGED:.*\.swiftmodule]]
// CHECK: PATH((bin/swiftc?(\.exe)?"?)) -modulewrap [[MERGED]]{{"?}} -target x86_64-unknown-linux-gnu -o [[OBJ:.*\.o]]
// CHECK: PATH((bin/clang.*)) [[OBJ]]
