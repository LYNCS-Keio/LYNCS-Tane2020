#define FILEPATH "./test.sock"
#include "server.h"
#include "unistd.h"

int main() {
  setup();
  while (true) {
    accept();
    read();
    write();
  }
  close();
  sleep(1);
  unlink();
}
