#include "oot3d/renderer/pica_texture_decode.h"
#include <chrono>
#include <iostream>
#include <random>
#include <stdexcept>
#include <utility>

namespace ReferenceOot3d::Renderer {
bool DecodePicaTextureRgba8(uint8_t, uint16_t, uint16_t, std::span<const uint8_t>,
                          std::vector<uint8_t>&, std::string*);
}
int main() {
    try {
        std::mt19937 random(128);
        const std::pair<uint16_t, uint16_t> dimensions[]{
            {0, 0}, {1, 1}, {7, 9}, {8, 8}, {9, 13}, {16, 32},
            {32, 16}, {64, 64}, {256, 128}, {512, 256}, {2048, 2048}};
        unsigned cases = 0;
        for (auto [w, h] : dimensions) {
            const auto size = size_t((w + 7) / 8) * ((h + 7) / 8) * 32;
            std::vector<uint8_t> bytes(size);
            for (auto& value : bytes) value = uint8_t(random());
            for (unsigned variant = 0; variant < 3; ++variant) {
                auto input = bytes;
                if (variant == 1 && !input.empty()) input.pop_back();
                if (variant == 2) input.push_back(0xff);
                std::vector<uint8_t> before, after;
                std::string a, b;
                auto oldOk = ReferenceOot3d::Renderer::DecodePicaTextureRgba8(11, w, h, input, before, &a);
                auto newOk = Oot3d::Renderer::DecodePicaTextureRgba8(11, w, h, input, after, &b);
                if (oldOk != newOk || before != after || a != b)
                    throw std::runtime_error("A4 result or error differs from the original decoder");
                ++cases;
            }
        }
        std::vector<uint8_t> packed(4096 * 2048 / 2);
        for (auto& value : packed) value = uint8_t(random());
        const auto measure = [&](auto decode) {
            std::vector<uint8_t> output;
            std::string error;
            decode(11, 4096, 2048, packed, output, &error);
            auto start = std::chrono::steady_clock::now();
            for (int i = 0; i < 8; ++i)
                if (!decode(11, 4096, 2048, packed, output, &error))
                    throw std::runtime_error(error);
            return std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - start).count() / 8;
        };
        const auto before = measure(ReferenceOot3d::Renderer::DecodePicaTextureRgba8);
        const auto after = measure(Oot3d::Renderer::DecodePicaTextureRgba8);
        std::cout << "equivalent_cases=" << cases << " original_ms=" << before
                  << " optimized_ms=" << after << " speedup=" << before / after << '\n';
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}