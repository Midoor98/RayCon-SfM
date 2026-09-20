#pragma once
// Small standalone utilities for the public preview. No private dependencies.
#include <algorithm>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace demo {
using Row = std::vector<std::string>;
inline std::string trim(std::string s) {
    const auto first = s.find_first_not_of(" \t\r\n");
    if (first == std::string::npos) return {};
    return s.substr(first, s.find_last_not_of(" \t\r\n") - first + 1);
}
inline Row split(const std::string& line) {
    Row fields;
    std::size_t start = 0;
    for (;;) {
        auto end = line.find(',', start);
        fields.push_back(trim(line.substr(start, end - start)));
        if (end == std::string::npos) return fields;
        start = end + 1;
    }
}
inline std::vector<Row> read_csv(const std::filesystem::path& path, const Row& header) {
    std::ifstream input(path);
    if (!input) throw std::runtime_error("cannot read input CSV");
    std::string line;
    if (!std::getline(input, line) || split(line) != header)
        throw std::runtime_error("unexpected CSV header (unquoted numeric CSV required)");
    std::vector<Row> rows;
    while (std::getline(input, line)) {
        if (trim(line).empty()) continue;
        auto row = split(line);
        if (row.size() != header.size()) throw std::runtime_error("invalid CSV field count");
        rows.push_back(std::move(row));
    }
    if (input.bad()) throw std::runtime_error("CSV read failed");
    if (rows.empty()) throw std::runtime_error("CSV contains no samples");
    return rows;
}
inline double number(const std::string& text) {
    std::size_t used = 0;
    double value = std::stod(text, &used);
    if (used != text.size() || !std::isfinite(value))
        throw std::runtime_error("expected finite numeric value");
    return value;
}
inline long long identifier(const std::string& text) {
    if (text.empty() || !std::all_of(text.begin(), text.end(), [](char c) { return c >= '0' && c <= '9'; }))
        throw std::runtime_error("expected nonnegative integer identifier");
    return std::stoll(text);
}
inline std::map<std::string, std::string> options(int argc, char** argv, bool tracks) {
    std::map<std::string, std::string> result;
    for (int i = 1; i < argc; ++i) {
        std::string key = argv[i];
        if (key != "--input" && key != "--output" && !(tracks && key == "--min-views"))
            throw std::runtime_error("unknown option: " + key);
        if (++i == argc) throw std::runtime_error("missing option value: " + key);
        result[key] = argv[i];
    }
    if (!result.count("--input") || !result.count("--output"))
        throw std::runtime_error("--input and --output are required; use --help");
    return result;
}
inline void create_output(const std::filesystem::path& path) {
    if (std::filesystem::exists(path) || std::filesystem::is_symlink(path))
        throw std::runtime_error("output directory already exists; choose a new directory");
    if (!std::filesystem::create_directories(path)) throw std::runtime_error("cannot create output directory");
}
inline void write(const std::filesystem::path& path, const std::string& text) {
    std::ofstream file(path);
    file.exceptions(std::ios::failbit | std::ios::badbit);
    file << text;
    file.close();
}
}  // namespace demo
