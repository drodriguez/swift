// RUN: %empty-directory(%t)
// RUN: %target-build-swift -index-file -index-file-path %s %s %S/Inputs/SwiftModuleA.swift -module-name unit_one_test -o %t/00-output_for_index -index-store-path %t/idx
// RUN: c-index-test core -print-unit %t/idx | %FileCheck %s -implicit-check-not SwiftShims

// The output is sorted by last path component, so make sure the top-level entry
// gets sorted first by prepending 0s.

// CHECK: 00-output_for_index
// CHECK: DEPEND START
// CHECK: Unit | system | Swift | [[MODULE:.*[/\\]Swift[.]swiftmodule([/\\].+[.]swiftmodule)?]] | [[SWIFT:.+[.]swiftmodule-[A-Z0-9]*]]
// CHECK: Record | user | PATH((.*/unit-one-file-multi-file-invocation.swift)) |
// CHECK: DEPEND END (2)

// CHECK: [[SWIFT]]
// CHECK: DEPEND START
// CHECK: Record | system | Swift.Math.Floating | [[MODULE]] | {{.+}}.swiftmodule_Math_Floating-{{.*}}
// CHECK: Record | system | Swift.String | [[MODULE]] | {{.+}}.swiftmodule_String-{{.*}}
// CHECK: DEPEND END

func test1() {
  funcSwiftA()
}
