cmake_minimum_required(VERSION 3.19)

if (PR)
    if (NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
        message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
        file(DOWNLOAD "https://raw.githubusercontent.com/conan-io/cmake-conan/v0.16.1/conan.cmake"
                "${CMAKE_BINARY_DIR}/conan.cmake"
                EXPECTED_HASH SHA256=396e16d0f5eabdc6a14afddbcfff62a54a7ee75c6da23f32f7a31bc85db23484
                TLS_VERIFY ON)
    endif ()
    include(${CMAKE_BINARY_DIR}/conan.cmake)
    # settings comes from parent project if possible
    # conan_cmake_autodetect(settings) requires compiler version to be defined first
    conan_cmake_install(PATH_OR_REFERENCE ${CMAKE_CURRENT_SOURCE_DIR}
            REMOTE ec2
            BUILD outdated
            PROFILE_HOST ${PR}
            PROFILE_BUILD default
            SETTINGS
            ${settings}
            build_type=${CMAKE_BUILD_TYPE}
            GENERATOR cmake
            )
    include(${CMAKE_CURRENT_BINARY_DIR}/conan_toolchain.cmake)
endif ()

project(larvio)
include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
#set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)

find_package(OpenCV REQUIRED)
find_package(Boost REQUIRED)
find_package(Ceres REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(SuiteSparse REQUIRED)
find_package(Pangolin REQUIRED)

include_directories(
    ${PROJECT_SOURCE_DIR}/include
    ${OpenCV_INCLUDE_DIRS}
    ${SUITESPARSE_INCLUDE_DIRS}
    ${CERES_INCLUDE_DIRS}
    ${Boost_INCLUDE_DIR}
    ${EIGEN3_INCLUDE_DIR}
    ${Pangolin_INCLUDE_DIRS}
)

# Image processor
add_library(image_processor
    ${PROJECT_SOURCE_DIR}/src/image_processor.cpp
    ${PROJECT_SOURCE_DIR}/src/ORBDescriptor.cpp
)
target_link_libraries(image_processor
    ${OpenCV_LIBRARIES}
)

# Initializer
# -- Static Initializer
add_library(staticInitializer
    ${PROJECT_SOURCE_DIR}/src/StaticInitializer.cpp
)
target_link_libraries(staticInitializer
    ${SUITESPARSE_LIBRARIES}
)
# -- Dynamic Initializer
add_library(dynamicInitializer
    ${PROJECT_SOURCE_DIR}/src/StaticInitializer.cpp
    ${PROJECT_SOURCE_DIR}/src/DynamicInitializer.cpp
    ${PROJECT_SOURCE_DIR}/src/feature_manager.cpp
    ${PROJECT_SOURCE_DIR}/src/initial_alignment.cpp
    ${PROJECT_SOURCE_DIR}/src/initial_sfm.cpp
    ${PROJECT_SOURCE_DIR}/src/solve_5pts.cpp
)
target_link_libraries(dynamicInitializer
    ${SUITESPARSE_LIBRARIES}
    ${CERES_LIBRARIES}
    ${OpenCV_LIBRARIES}
)
# -- Flexible Initializer
add_library(flexibleInitializer
    ${PROJECT_SOURCE_DIR}/src/FlexibleInitializer.cpp
)
target_link_libraries(flexibleInitializer
    staticInitializer
    dynamicInitializer
)

# Estimator
add_library(estimator
    ${PROJECT_SOURCE_DIR}/src/larvio.cpp
)
target_link_libraries(estimator
    flexibleInitializer
    ${SUITESPARSE_LIBRARIES}
    ${OpenCV_LIBRARIES}
)

# App
add_executable(larvio app/larvioMain.cpp)
target_link_libraries(larvio 
    image_processor 
    estimator
    ${OpenCV_LIBS}
    ${Pangolin_LIBRARIES}
)