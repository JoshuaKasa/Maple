#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <random>
#include <chrono>
#include <map>
#include <cstdint>

namespace sugar {
int64_t pow(int64_t base, int64_t power) {
int64_t result = 1;
for (int i = 0; i < power; i++) {
result *= base;
}
std::cout << result << std::endl;
}
int64_t fact(int64_t n) {
if (n <= 1) {
std::cout << 1 << std::endl;
}
int64_t prev = 1;
n += 1;
for (int i = 2; i < n; i++) {
prev *= i;
}
std::cout << prev << std::endl;
}
int64_t evnodd(int64_t n) {
n %= 2;
if (n == 0) {
std::cout << true << std::endl;
}
else {
std::cout << false << std::endl;
}
}
}
