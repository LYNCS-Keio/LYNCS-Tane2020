#include <pybind11/pybind11.h>
#include "ttt.hpp"

namespace py = pybind11;

PYBIND11_MODULE(ttt, t) {
    py::module m("t_t", "pybind11 plugin");
    py::class_<Test>(t, "ttt")
        .def(py::init())
}