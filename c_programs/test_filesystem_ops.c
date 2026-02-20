#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

void process_entry(const char *path, const char *name) {
    char full_path[4096];
    struct stat st;
    int fd;
    char buffer[1];

    if (path[strlen(path)-1] == '/') {
        snprintf(full_path, sizeof(full_path), "%s%s", path, name);
    } else {
        snprintf(full_path, sizeof(full_path), "%s/%s", path, name);
    }

    printf("[CHECK] %s\n", full_path);
    fflush(stdout);

    // 1. lstat
    printf("  -> lstat...\n");
    fflush(stdout);
    if (lstat(full_path, &st) == -1) {
        perror("  LSTAT FAILED");
        return; // Don't proceed if lstat fails
    }

    // Only process regular files for open/read
    if (S_ISREG(st.st_mode)) {
        // 2. open
        printf("  -> open...\n");
        fflush(stdout);
        fd = open(full_path, O_RDONLY);
        if (fd == -1) {
            perror("  OPEN FAILED");
        } else {
            // 3. read (1 byte)
            printf("  -> read...\n");
            fflush(stdout);
            ssize_t bytes_read = read(fd, buffer, 1);
            if (bytes_read == -1) {
                perror("  READ FAILED");
            } else {
                printf("    (read %zd bytes)\n", bytes_read);
            }
            
            // 4. close
            close(fd);
        }
    } else if (S_ISLNK(st.st_mode)) {
        // 2. readlink
        char link_target[4096];
        printf("  -> readlink...\n");
        fflush(stdout);
        ssize_t len = readlink(full_path, link_target, sizeof(link_target) - 1);
        if (len != -1) {
            link_target[len] = '\0';
            printf("    (link target: %s)\n", link_target);
        } else {
            perror("  READLINK FAILED");
        }
    } else if (S_ISDIR(st.st_mode)) {
        // Recurse into subdirectories (skip . and ..)
        if (strcmp(name, ".") != 0 && strcmp(name, "..") != 0) {
           // We will handle recursion in the traverse_directory function roughly, 
           // but actually it's cleaner to have a separate traversal function.
           // However, for this simple test, we'll just let the traversing logic handle it.
           // Wait, this function processes a *single entry*. 
           // If it's a directory, we should probably recurse here or rely on the caller.
           // Let's implement recursion here.
           
           printf("  -> Start recursion into %s\n", full_path);
           DIR *sub_dir = opendir(full_path);
           if (!sub_dir) {
               perror("  OPENDIR FAILED");
               return;
           }

           struct dirent *sub_entry;
           while ((sub_entry = readdir(sub_dir)) != NULL) {
               process_entry(full_path, sub_entry->d_name);
           }
           closedir(sub_dir);
           printf("  <- End recursion into %s\n", full_path);
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <directory_path>\n", argv[0]);
        return 1;
    }

    const char *start_path = argv[1];
    struct stat st;

    // Initial check of the start path
    if (lstat(start_path, &st) == -1) {
        perror("Initial lstat failed");
        return 1;
    }

    if (S_ISDIR(st.st_mode)) {
        printf("Starting recursive traversal from: %s\n", start_path);
        
        DIR *dir = opendir(start_path);
        if (!dir) {
            perror("opendir failed");
            return 1;
        }

        struct dirent *entry;
        while ((entry = readdir(dir)) != NULL) {
           process_entry(start_path, entry->d_name);
        }
        closedir(dir);
    } else {
        // Process single file
        // We need to split path and name, but for simplicity just pass empty path and full name
        process_entry("", start_path);
    }

    printf("Traversal complete.\n");
    return 0;
}
