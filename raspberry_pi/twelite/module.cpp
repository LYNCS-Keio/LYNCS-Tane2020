#include <pybind11/pybind11.h>
#include "send_recv.cpp"

PYBIND11_MODULE(twelite_module, m) {
    m.doc() = "twelite module test";
    m.def("send_recv", &send_recv, "send and recv");
}