// https://www.geekpage.jp/programming/linux-network/book/07/7-9.php

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

int main() {
  int sock;
  struct sockaddr_un s_un;
  int n;
  char buf[128];

  sock= socket(AF_UNIX, SOCK_STREAM, 0);
  if (sock < 0) {
    perror("socket");
    return 1;
  }

  s_un.sun_family = AF_UNIX;
  strcpy(s_un.sun_path, "test.sock");

  if (connect(sock, (struct sockaddr *)&s_un, sizeof(s_un)) != 0) {
    perror("connect");
    return 1;
  }

  printf("after connect\n");

  write(sock, "Hello", 4);
  memset(buf, 0, sizeof(buf));
  n = read(sock, buf, sizeof(buf));
  if (n < 0) {
    perror("read");
    return 1;
  }

  printf("%s\n", buf);

  close(sock);

  return 0;
}
