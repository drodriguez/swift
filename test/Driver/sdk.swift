// RUN: %swiftc_driver -driver-print-jobs -target x86_64-apple-macosx10.9     -g -sdk %S/../Inputs/clang-importer-sdk %s 2>&1 | %FileCheck %s --check-prefix OSX
// RUN: %swiftc_driver -driver-print-jobs -target x86_64-unknown-linux-gnu    -g -sdk %S/../Inputs/clang-importer-sdk %s 2>&1 | %FileCheck %s --check-prefix LINUX
// RUN: %swiftc_driver -driver-print-jobs -target x86_64-unknown-freebsd      -g -sdk %S/../Inputs/clang-importer-sdk %s 2>&1 | %FileCheck %s --check-prefix FREEBSD
// RUN: %swiftc_driver -driver-print-jobs -target x86_64-unknown-windows-msvc -g -sdk %S/../Inputs/clang-importer-sdk %s 2>&1 | %FileCheck %s --check-prefix WINDOWS
// RUN: %swiftc_driver -driver-print-jobs -target wasm32-unknown-wasi         -g -sdk %S/../Inputs/clang-importer-sdk %s 2>&1 | %FileCheck %s --check-prefix WASI

// RUN: env SDKROOT=%S/../Inputs/clang-importer-sdk %swiftc_driver_plain -target x86_64-apple-macosx10.9  -g -driver-print-jobs %s 2>&1 | %FileCheck %s --check-prefix OSX
// RUN: env SDKROOT=%S/../Inputs/clang-importer-sdk %swiftc_driver_plain -target x86_64-unknown-linux-gnu -g -driver-print-jobs %s 2>&1 | %FileCheck %s --check-prefix LINUX
// RUN: env SDKROOT=%S/../Inputs/clang-importer-sdk %swiftc_driver_plain -target x86_64-unknown-freebsd   -g -driver-print-jobs %s 2>&1 | %FileCheck %s --check-prefix FREEBSD

// OSX-NOT: warning: no such SDK:
// OSX: PATH((bin/swift))
// OSX: PATH((Driver/sdk.swift))
// OSX: -sdk {{.*}}/Inputs/clang-importer-sdk
// OSX-NEXT: PATH((bin/swift))
// OSX: -sdk {{.*}}/Inputs/clang-importer-sdk
// OSX: {{.*}}.o{{[ "]}}
// OSX: {{-syslibroot|--sysroot}} {{[^ ]*}}/Inputs/clang-importer-sdk
// OSX: -L PATH(([^ ]*/Inputs/clang-importer-sdk/usr/lib/swift))

// LINUX-NOT: warning: no such SDK:
// LINUX: PATH((bin/swift))
// LINUX: PATH((Driver/sdk.swift))
// LINUX: -sdk {{.*}}/Inputs/clang-importer-sdk
// LINUX-NEXT: PATH((bin/swift))
// LINUX: -sdk {{.*}}/Inputs/clang-importer-sdk
// LINUX: PATH((.*swiftrt.o))
// LINUX: {{-syslibroot|--sysroot}} {{.*}}/Inputs/clang-importer-sdk

// FREEBSD-NOT: warning: no such SDK:
// FREEBSD: PATH((bin/swift))
// FREEBSD: PATH((Driver/sdk.swift))
// FREEBSD: -sdk {{.*}}/Inputs/clang-importer-sdk
// FREEBSD-NEXT: PATH((bin/swift))
// FREEBSD: -sdk {{.*}}/Inputs/clang-importer-sdk
// FREEBSD: {{.*}}swiftrt.o
// FREEBSD: {{-syslibroot|--sysroot}} {{.*}}/Inputs/clang-importer-sdk

// WINDOWS-NOT: warning: no such SDK:
// WINDOWS: PATH((bin/swift))
// WINDOWS: PATH((Driver/sdk.swift))
// WINDOWS: -sdk {{.*}}/Inputs/clang-importer-sdk
// WINDOWS-NEXT: PATH((bin/swift))
// WINDOWS: -sdk {{.*}}/Inputs/clang-importer-sdk
// WINDOWS: {{.*}}Inputs/clang-importer-sdk{{.*}}swiftrt.o
// WINDOWS: {{-I}} {{.*}}/Inputs/clang-importer-sdk

// WASI-NOT: warning: no such SDK:
// WASI: PATH((bin/swift))
// WASI: PATH((Driver/sdk.swift))
// WASI: -sdk {{.*}}/Inputs/clang-importer-sdk
// WASI-NEXT: PATH((bin/swift))
// WASI: -sdk {{.*}}/Inputs/clang-importer-sdk
// WASI: {{-syslibroot|--sysroot}} {{.*}}/Inputs/clang-importer-sdk

// RUN: %swift_driver -driver-print-jobs -repl -sdk %S/Inputs/nonexistent-sdk 2>&1 | %FileCheck %s --check-prefix=SDKWARNING
// RUN: %swift_driver -driver-print-jobs -sdk %S/Inputs/nonexistent-sdk 2>&1 | %FileCheck %s --check-prefix=SDKWARNING
// RUN: env SDKROOT=%S/Inputs/nonexistent-sdk %swift_driver_plain -driver-print-jobs -repl 2>&1 | %FileCheck %s --check-prefix=SDKWARNING

// SDKWARNING: warning: no such SDK: '{{.*}}/Inputs/nonexistent-sdk'
// SDKWARNING: -sdk {{.*}}/Inputs/nonexistent-sdk

// RUN: %swiftc_driver -driver-print-jobs -typecheck -sdk %S/../Inputs/clang-importer-sdk -module-cache-path /path/to/cache %s 2>&1 | %FileCheck %s --check-prefix=CACHE-PATH

// CACHE-PATH: -module-cache-path /path/to/cache
