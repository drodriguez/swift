// RUN: not %swift -c %s -vfsoverlay first-missing-overlay.yaml -vfsoverlay next-missing-overlay.yaml -vfsoverlay final-missing-overlay.yaml 2>&1 | %FileCheck %s -check-prefix=MISSING_VFS_OVERLAYS
// RUN: not %swift -c %s -vfsoverlay %S/Inputs/invalid-overlay.yaml 2>&1 | %FileCheck %s -check-prefix=INVALID_VFS_OVERLAY

// MISSING_VFS_OVERLAYS: <unknown>:0: error: cannot open file 'PATH(({{.*}}/first-missing-overlay.yaml))' ({{[Nn]}}o such file or directory)
// MISSING_VFS_OVERLAYS-NEXT: <unknown>:0: error: cannot open file 'PATH(({{.*}}/next-missing-overlay.yaml))' ({{[Nn]}}o such file or directory)
// MISSING_VFS_OVERLAYS-NEXT: <unknown>:0: error: cannot open file 'PATH(({{.*}}/final-missing-overlay.yaml))' ({{[Nn]}}o such file or directory)

// INVALID_VFS_OVERLAY: <unknown>:0: error: invalid virtual overlay file 'PATH(({{.*}}/invalid-overlay.yaml))'
