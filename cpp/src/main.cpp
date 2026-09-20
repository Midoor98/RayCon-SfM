#include "demo_io.hpp"
#include <iostream>
#include <set>
#include <utility>

using Node = std::pair<long long, long long>;
using Component = std::vector<Node>;

std::string observations(const Component& component) {
    std::ostringstream text;
    text << '[';
    for (std::size_t i = 0; i < component.size(); ++i) {
        if (i) text << ',';
        text << "{\"image_id\":" << component[i].first << ",\"feature_id\":" << component[i].second << '}';
    }
    return text.str() + ']';
}

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--version") {
            std::cout << "RayCon-SfM public preview " << DEMO_VERSION << '\n';
            return 0;
        }
        if (argc == 2 && std::string(argv[1]) == "--help") {
            std::cout << "Feature association utilities; no camera or structure estimation.\n"
                         "Usage: raycon_sfm_preview --input pairs.csv --output NEW_DIRECTORY [--min-views 2]\n";
            return 0;
        }
        auto args = demo::options(argc, argv, true);
        long long min_views = args.count("--min-views") ? demo::identifier(args.at("--min-views")) : 2;
        if (min_views < 2) throw std::runtime_error("min-views must be at least two");
        auto rows = demo::read_csv(args.at("--input"), {"image_a", "feature_a", "image_b", "feature_b"});
        std::map<Node, std::set<Node>> adjacency;
        std::set<std::pair<Node, Node>> edges;
        std::set<long long> images;
        std::size_t duplicates = 0;
        for (const auto& row : rows) {
            Node a{demo::identifier(row[0]), demo::identifier(row[1])};
            Node b{demo::identifier(row[2]), demo::identifier(row[3])};
            if (a.first == b.first) throw std::runtime_error("matches must connect different images");
            if (!edges.insert({std::min(a, b), std::max(a, b)}).second) { ++duplicates; continue; }
            adjacency[a].insert(b); adjacency[b].insert(a);
            images.insert(a.first); images.insert(b.first);
        }
        std::set<Node> visited;
        std::vector<Component> tracks;
        std::vector<std::pair<std::string, Component>> rejected;
        for (const auto& item : adjacency) {
            if (!visited.insert(item.first).second) continue;
            Component stack{item.first}, component;
            while (!stack.empty()) {
                Node node = stack.back(); stack.pop_back(); component.push_back(node);
                for (const auto& neighbor : adjacency.at(node))
                    if (visited.insert(neighbor).second) stack.push_back(neighbor);
            }
            std::sort(component.begin(), component.end());
            std::set<long long> image_ids;
            for (const auto& node : component) image_ids.insert(node.first);
            if (image_ids.size() != component.size())
                rejected.push_back({"multiple_features_in_one_image", component});
            else if (component.size() < static_cast<unsigned long long>(min_views))
                rejected.push_back({"too_few_views", component});
            else tracks.push_back(component);
        }
        std::ostringstream track_json, rejected_json, visibility, summary;
        track_json << '['; rejected_json << '[';
        visibility << "track_id,image_id,feature_id\n";
        std::map<std::size_t, std::size_t> histogram;
        for (std::size_t i = 0; i < tracks.size(); ++i) {
            if (i) track_json << ',';
            track_json << "\n{\"track_id\":" << i << ",\"observations\":" << observations(tracks[i]) << '}';
            ++histogram[tracks[i].size()];
            for (const auto& node : tracks[i]) visibility << i << ',' << node.first << ',' << node.second << '\n';
        }
        for (std::size_t i = 0; i < rejected.size(); ++i) {
            if (i) rejected_json << ',';
            rejected_json << "\n{\"reason\":\"" << rejected[i].first << "\",\"observations\":" << observations(rejected[i].second) << '}';
        }
        track_json << "\n]\n"; rejected_json << "\n]\n";
        summary << "{\n  \"version\": \"" << DEMO_VERSION << "\",\n"
                << "  \"mode\": \"public-demo\",\n  \"backend\": \"cpp_feature_graph_components\",\n"
                << "  \"input_match_count\": " << rows.size() << ",\n  \"unique_match_count\": " << edges.size()
                << ",\n  \"duplicate_match_count\": " << duplicates << ",\n  \"input_image_count\": " << images.size()
                << ",\n  \"accepted_track_count\": " << tracks.size() << ",\n  \"rejected_component_count\": " << rejected.size()
                << ",\n  \"min_views\": " << min_views << ",\n  \"track_length_histogram\": {";
        bool first = true;
        for (const auto& item : histogram) {
            if (!first) summary << ',';
            summary << '"' << item.first << "\":" << item.second;
            first = false;
        }
        summary << "},\n  \"camera_estimation\": false,\n  \"point_triangulation\": false\n}\n";
        const std::filesystem::path output = args.at("--output");
        demo::create_output(output);
        demo::write(output / "tracks.json", track_json.str());
        demo::write(output / "rejected.json", rejected_json.str());
        demo::write(output / "visibility.csv", visibility.str());
        demo::write(output / "summary.json", summary.str());
        std::cout << "RayCon-SfM v" << DEMO_VERSION << " | public preview\n"
                  << "Organized " << tracks.size() << " tracks. Output: " << output << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Input/output error: " << error.what() << '\n';
        return 2;
    }
}
