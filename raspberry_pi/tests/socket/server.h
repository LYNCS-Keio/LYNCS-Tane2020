// https://www.geekpage.jp/programming/linux-network/book/07/7-9.php

#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

void setup() {
  remove(FILEPATH);

  if (s0 < 0) {
    perror("socket");
    return 1;
  }
  s_un.sun_family = AF_UNIX;

  strcpy(s_un.sun_path, FILEPATH);

  if (bind(s0, (struct sockaddr *)&s_un, sizeof(s_un)) != 0) {
    perror("bind");
    return 1;
  }

  if (listen(s0, 5) != 0) {
    perror("listen");
    return 1;
  }
}

void accept() {
  addrlen = sizeof(s_un_accept);

  sock = accept(s0, (struct sockaddr *)&s_un_accept, &addrlen);
  if (sock < 0) {
    perror("accept");
    return 1;
  }

  printf("after accept\n");
}

void read() {
  memset(buf, 0, sizeof(buf));
  n = read(sock, buf, sizeof(buf));
}

void write() {
  printf ("%s\n", buf);
  write(sock, "HOGE", 4);

  close(sock);
  close(s0);
}

void unlink() {
  unlink(FILEPATH);

  return 0;
}