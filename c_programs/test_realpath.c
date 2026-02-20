#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <errno.h>
#include <string.h>

double get_time_ms() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1000000.0;
}

void test_path(const char *path) {
    char resolved[4096];
    double start, end;

    printf("Testing realpath for: '%s'\n", path);
    start = get_time_ms();
    if (realpath(path, resolved) != NULL) {
        end = get_time_ms();
        printf("  SUCCESS: %s (took %.3f ms)\n", resolved, end - start);
    } else {
        end = get_time_ms();
        fprintf(stderr, "  FAILED: %s (took %.3f ms)\n", strerror(errno), end - start);
    }
}

int main(int argc, char *argv[]) {
    if (argc > 1) {
        for (int i = 1; i < argc; i++) {
            test_path(argv[i]);
        }
    } else {
        test_path(".");
        test_path("..");
        test_path(".git");
    }
    return 0;
}
