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

#include "../../../lib/sugar.hpp"
namespace fibonacci {
void fibonacci(int32_t n) {
int32_t a = 0;
int32_t b = 1;
int32_t c = 0;
for (int i = 1; i < n; i++) {
c = a + b;
a = b;
b = c;
std::cout << c << std::endl;
}
}
}
int main() {
std::map<std::string, int8_t> backups;
sugar::evnodd(11);
if (1 == 1) {
std::cout << 1 << std::endl;
}
else {
std::cout << 0 << std::endl;
}

std::cin.get();
return 0;
}
