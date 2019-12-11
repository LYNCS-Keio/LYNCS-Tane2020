#include <pybind11/pybind11.h>
#include "twelite.hpp"

namespace py = pybind11;

PYBIND11_MODULE(twelite, t) {
    py::module m("twe_twe", "pybind11 plugin");
    py::class_<TWE_Lite>(t, "twe_lite")
        .def(py::init())
        .def("send_simple", &TWE_Lite::send_simple)
        .def("send_buf_simple", &TWE_Lite::send_buf_simple)
        .def("do_send", &TWE_Lite::do_send)
        .def("check_send", &TWE_Lite::check_send)
        .def("get_data", &TWE_Lite::get_data)
        .def("recv", &TWE_Lite::recv)
        .def("recv", &TWE_Lite::recv)
        .def("try_recv", &TWE_Lite::try_recv)
        .def("try_recv8", &TWE_Lite::try_recv8)
}