#define FILEPATH "./test.sock"
#include "server.h"

int main() {
    setup();
    accept();
    read();
    write();
    unlink();
}