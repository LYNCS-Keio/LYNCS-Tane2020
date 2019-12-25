#define FILEPATH "./test.sock"
#include "server.h"

int s0, sock;
struct sockaddr_un s_un;
struct sockaddr_un s_un_accept;
socklen_t addrlen;
s0 = socket(AF_UNIX, SOCK_STREAM, 0);

char buf[1024];
int flag;
int n;

int main() {
    setup();
    accept();
    read();
    write();
    unlink();
}