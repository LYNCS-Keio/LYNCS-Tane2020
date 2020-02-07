#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "send_recv.cc"

PYBIND11_MODULE(send_recv, m) {
    m.doc() = "twelite module test";
    m.def("send_recv", &send_recv, "send and recv");
}
