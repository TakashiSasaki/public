#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>
#include <windows.h>
#include <time.h>
#include <errno.h>
#include <direct.h>

#define ARRAY_SIZE(x) (sizeof(x)/sizeof(x[0]))

double get_time_ms() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1000000.0;
}

static void convert_slashes(char *path) {
    for (; *path; path++)
        if (*path == '\\')
            *path = '/';
}

static int xwcstoutf(char *utf, const wchar_t *w, size_t n) {
    int ret = WideCharToMultiByte(CP_UTF8, 0, w, -1, utf, n, NULL, NULL);
    if (ret <= 0)
        return -1;
    return ret;
}

char *mingw_getcwd_test(char *pointer, int len) {
    wchar_t wpointer[MAX_PATH];
    if (!_wgetcwd(wpointer, ARRAY_SIZE(wpointer)))
        return NULL;
    if (xwcstoutf(pointer, wpointer, len) < 0)
        return NULL;
    convert_slashes(pointer);
    return pointer;
}

int main() {
    char buffer[4096];
    double start, end;

    printf("Starting mingw_getcwd logic test...\n");

    for (int i = 0; i < 5; i++) {
        start = get_time_ms();
        if (mingw_getcwd_test(buffer, sizeof(buffer)) != NULL) {
            end = get_time_ms();
            printf("[%d] mingw_getcwd success: %s (took %.3f ms)\n", i + 1, buffer, end - start);
        } else {
            end = get_time_ms();
            printf("[%d] mingw_getcwd failed (took %.3f ms)\n", i + 1, end - start);
        }
    }

    return 0;
}
