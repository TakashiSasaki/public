#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
#include <string.h>

double get_time_ms() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1000000.0;
}

int main() {
    char cwd[4096];
    double start, end;

    printf("Starting getcwd test...\n");

    for (int i = 0; i < 5; i++) {
        start = get_time_ms();
        if (getcwd(cwd, sizeof(cwd)) != NULL) {
            end = get_time_ms();
            printf("[%d] getcwd success: %s (took %.3f ms)\n", i + 1, cwd, end - start);
        } else {
            end = get_time_ms();
            fprintf(stderr, "[%d] getcwd failed: %s (took %.3f ms)\n", i + 1, strerror(errno), end - start);
        }
    }

    return 0;
}
