#include <stdio.h>
#include <windows.h>
#include <time.h>

double get_time_ms() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1000000.0;
}

void test_long_path(const wchar_t *path) {
    wchar_t long_path[4096];
    double start, end;

    printf("Testing GetLongPathNameW for: '%ls'\n", path);
    start = get_time_ms();
    DWORD ret = GetLongPathNameW(path, long_path, 4096);
    end = get_time_ms();

    if (ret > 0 && ret < 4096) {
        printf("  SUCCESS: %ls (took %.3f ms)\n", long_path, end - start);
    } else {
        printf("  FAILED: error %lu (took %.3f ms)\n", GetLastError(), end - start);
    }
}

int main() {
    wchar_t cwd[4096];
    if (GetCurrentDirectoryW(4096, cwd)) {
        test_long_path(cwd);
        
        // Test with a potential subfolder
        wchar_t git_path[4096];
        swprintf(git_path, 4096, L"%ls\\.git", cwd);
        test_long_path(git_path);
    } else {
        printf("GetCurrentDirectoryW failed\n");
    }

    return 0;
}
