PROJECT(MyHello)
cmake_minimum_required(VERSION 2.8)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP()


IF(NOT WIN32)
    SET(CMAKE_CXX_FLAGS "-std=c++0x")
    ADD_EXECUTABLE(calculator_client calculator.capnp.c++ calculator-client.c++)
    ADD_EXECUTABLE(calculator_server calculator.capnp.c++ calculator-server.c++)
    
    include_directories(${CONAN_INCLUDE_DIRS})
    target_link_libraries(calculator_client ${CONAN_LIBS})
    target_link_libraries(calculator_server ${CONAN_LIBS})
ENDIF()


