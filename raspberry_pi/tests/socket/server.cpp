#define FILEPATH "./test.sock"
#include "server.h"
#include "unistd.h"

int main() {
  setup();
  accept();

  while (true) {
    read();
    write();
  }

  close();
  unlink();
}
