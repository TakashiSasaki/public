#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <sys/stat.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>

#define LATENCY_THRESHOLD_NS 10000000 // 10ms

long long current_timestamp_ns() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

void process_directory(const char *path) {
    long long start, end, duration;
    char full_path[4096];
    struct stat st;
    struct dirent *entry;
    DIR *dir;

    printf("[INFO] Entering directory: %s\n", path);

    // Measure opendir
    start = current_timestamp_ns();
    dir = opendir(path);
    end = current_timestamp_ns();
    duration = end - start;

    if (!dir) {
        perror("opendir failed");
        return;
    }

    if (duration > LATENCY_THRESHOLD_NS) {
        printf("[WARN] opendir took %.3f ms for %s\n", duration / 1000000.0, path);
    }

    while (1) {
        // Measure readdir
        errno = 0;
        start = current_timestamp_ns();
        entry = readdir(dir);
        end = current_timestamp_ns();
        duration = end - start;

        if (!entry) {
            if (errno != 0) {
                perror("readdir failed");
            }
            break;
        }

        if (duration > LATENCY_THRESHOLD_NS) {
            printf("[WARN] readdir took %.3f ms for entry in %s\n", duration / 1000000.0, path);
        }

        // Construct full path
        if (strcmp(path, "/") == 0) {
             snprintf(full_path, sizeof(full_path), "/%s", entry->d_name);
        } else if (path[strlen(path)-1] == '/') {
             snprintf(full_path, sizeof(full_path), "%s%s", path, entry->d_name);
        } else {
             snprintf(full_path, sizeof(full_path), "%s/%s", path, entry->d_name);
        }

        // Measure lstat
        start = current_timestamp_ns();
        int res = lstat(full_path, &st);
        end = current_timestamp_ns();
        duration = end - start;

        if (res == -1) {
            perror("lstat failed");
            continue;
        }

        if (duration > LATENCY_THRESHOLD_NS) {
            printf("[WARN] lstat took %.3f ms for %s\n", duration / 1000000.0, full_path);
        }

        // Check for symlink and measure readlink
        if (S_ISLNK(st.st_mode)) {
            char link_target[4096];
            start = current_timestamp_ns();
            ssize_t len = readlink(full_path, link_target, sizeof(link_target) - 1);
            end = current_timestamp_ns();
            duration = end - start;

            if (len != -1) {
                link_target[len] = '\0';
                if (duration > LATENCY_THRESHOLD_NS) {
                    printf("[WARN] readlink took %.3f ms for %s -> %s\n", duration / 1000000.0, full_path, link_target);
                }
            } else {
                perror("readlink failed");
            }
        }

        // Recurse on directories
        if (S_ISDIR(st.st_mode)) {
            if (strcmp(entry->d_name, ".") != 0 && strcmp(entry->d_name, "..") != 0 && strcmp(entry->d_name, ".git") != 0) {
                process_directory(full_path);
            }
        }
    }

    closedir(dir);
}

int main(int argc, char *argv[]) {
    // Disable stdout buffering
    setvbuf(stdout, NULL, _IONBF, 0);

    if (argc < 2) {
        fprintf(stderr, "Usage: %s <directory_path>\n", argv[0]);
        return 1;
    }

    printf("Starting traversal of %s...\n", argv[1]);
    printf("Logging operations taking longer than 10ms...\n");

    process_directory(argv[1]);

    printf("Traversal complete.\n");
    return 0;
}
