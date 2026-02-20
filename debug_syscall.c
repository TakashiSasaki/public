#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <sys/stat.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <directory_path>\n", argv[0]);
        return 1;
    }

    const char *dir_path = argv[1];
    printf("Opening directory: %s\n", dir_path);

    DIR *dir = opendir(dir_path);
    if (!dir) {
        perror("opendir failed");
        return 1;
    }

    struct dirent *entry;
    struct stat st;
    char full_path[4096];
    int count = 0;

    printf("Iterating entries...\n");

    while (1) {
        printf("[DEBUG] Calling readdir...\n");
        errno = 0;
        entry = readdir(dir);
        
        if (!entry) {
            if (errno != 0) {
                perror("readdir failed");
            } else {
                printf("End of directory reached.\n");
            }
            break;
        }

        printf("[DEBUG] Found entry: '%s'\n", entry->d_name);

        // Construct full path
        snprintf(full_path, sizeof(full_path), "%s/%s", dir_path, entry->d_name);

        printf("[DEBUG] calling lstat on '%s'...\n", full_path);
        if (lstat(full_path, &st) == -1) {
            perror("lstat failed");
        } else {
            printf("[DEBUG] lstat success. Mode: %o, Size: %lld\n", st.st_mode, (long long)st.st_size);
        }

        count++;
        // Flush stdout to ensure we see the last message before a hang
        fflush(stdout);
    }

    closedir(dir);
    printf("Processed %d entries.\n", count);
    return 0;
}
