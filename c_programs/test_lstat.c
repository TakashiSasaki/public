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

        printf("[%d] Found entry: '%s'\n", count, entry->d_name);

        // Construct full path
        // rudimentary path joining
        if (dir_path[strlen(dir_path)-1] == '/' || dir_path[strlen(dir_path)-1] == '\\') {
             snprintf(full_path, sizeof(full_path), "%s%s", dir_path, entry->d_name);
        } else {
             snprintf(full_path, sizeof(full_path), "%s/%s", dir_path, entry->d_name);
        }

        printf("    calling lstat on '%s'...\n", full_path);
        if (lstat(full_path, &st) == -1) {
            perror("    lstat failed");
        } else {
            printf("    lstat success. Mode: %o, Size: %lld, Inode: %llu\n", st.st_mode, (long long)st.st_size, (unsigned long long)st.st_ino);
        }

        count++;
        fflush(stdout);
    }

    closedir(dir);
    printf("Processed %d entries.\n", count);
    return 0;
}
