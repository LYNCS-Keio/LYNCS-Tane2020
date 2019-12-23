#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <iostream>
#define RASPBERRY_PI
#include "twelite.hpp"

TWE_Lite twelit("/dev/ttyS0", 115200);

int send_recv(){
	twelit.init();

	uint8_t buf[] = { 'A', 'B' };
	while(true){
		std::cout << "send: ";
//		twelit.recv();
		twelit.send_buf_extend(0x00, 0x01, buf, 2);
		if(twelit.check_send())
			std::cout << "ok";
		else
			std::cout << "fail";
		std::cout << std::endl;

		delay(100);
continue;
		const size_t size = twelit.recv();
		if(size == 0) continue;
		std::cout << "recv: ";
		for(size_t i=0;i<size;i++){
//			std::cout << std::hex << (uint32_t)twelit.recv_buf[i];
		}
		std::cout << std::endl;
	}

	return 0;
}
