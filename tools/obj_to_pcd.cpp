// Simple OBJ -> PCD (ASCII) converter with normals
// - Loads an OBJ via tinyobjloader
// - Uses provided vertex normals if available; otherwise computes vertex normals by averaging face normals
// - Writes ASCII PCD with fields: x y z normal_x normal_y normal_z

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cmath>
#include <unordered_map>
#include <sstream>

#define TINYOBJLOADER_IMPLEMENTATION
#include "../tiny_obj_loader.h"

struct Vec3 {
    double x{0}, y{0}, z{0};
    Vec3() = default;
    Vec3(double X, double Y, double Z) : x(X), y(Y), z(Z) {}
    Vec3 operator+(const Vec3 &o) const { return Vec3(x+o.x, y+o.y, z+o.z); }
    Vec3& operator+=(const Vec3 &o) { x+=o.x; y+=o.y; z+=o.z; return *this; }
    Vec3 operator-(const Vec3 &o) const { return Vec3(x-o.x, y-o.y, z-o.z); }
    Vec3 operator*(double s) const { return Vec3(x*s, y*s, z*s); }
};

static inline Vec3 cross(const Vec3& a, const Vec3& b){
    return Vec3(a.y*b.z - a.z*b.y, a.z*b.x - a.x*b.z, a.x*b.y - a.y*b.x);
}
static inline double dot(const Vec3& a, const Vec3& b){ return a.x*b.x + a.y*b.y + a.z*b.z; }
static inline double norm(const Vec3& a){ return std::sqrt(dot(a,a)); }
static inline Vec3 normalize(const Vec3& a){ double n = norm(a); if(n<=0) return Vec3(0,0,1); return a*(1.0/n); }

int main(int argc, char** argv){
    if(argc < 3){
        std::cerr << "Usage: " << argv[0] << " <input.obj> <output.pcd>\n";
        return 1;
    }
    std::string input = argv[1];
    std::string output = argv[2];

    tinyobj::attrib_t attrib;
    std::vector<tinyobj::shape_t> shapes;
    std::vector<tinyobj::material_t> materials;
    std::string warn, err;
    // Use legacy tinyobj LoadObj API available in this repo's header
    // Args: attrib, shapes, materials, warn, err, filename, mtl_basepath, triangulate, default_vcols_fallback
    bool ret = tinyobj::LoadObj(&attrib, &shapes, &materials, &warn, &err, input.c_str(), /*mtl_basepath*/ nullptr, /*triangulate*/ false, /*default_vcols_fallback*/ false);
    if(!warn.empty()) std::cerr << warn << "\n";
    if(!ret){
        std::cerr << "Failed to load OBJ: " << input << "\n" << err << "\n";
        return 2;
    }

    size_t numVerts = attrib.vertices.size() / 3;
    if(numVerts == 0){
        std::cerr << "No vertices in OBJ: " << input << "\n";
        return 3;
    }

    std::vector<Vec3> V(numVerts);
    for(size_t i=0;i<numVerts;i++){
        V[i] = Vec3(attrib.vertices[3*i+0], attrib.vertices[3*i+1], attrib.vertices[3*i+2]);
    }

    bool hasVN = (attrib.normals.size()/3) >= numVerts; // Often not guaranteed to match by index
    std::vector<Vec3> VN(numVerts, Vec3(0,0,0));
    std::vector<int> VNcount(numVerts, 0);

    if(hasVN){
        // Attempt to map normals by per-index usage (more reliable)
        // Fallback: if normal indices absent, try direct mapping by vertex index
        bool haveNormalIndices = false;
        for(const auto& s : shapes){ if(!s.mesh.indices.empty() && s.mesh.indices[0].normal_index >= 0) { haveNormalIndices = true; break; } }
        if(haveNormalIndices){
            for(const auto& s : shapes){
                size_t idx_offset = 0;
                for(size_t f=0; f < s.mesh.num_face_vertices.size(); f++){
                    unsigned char fv = s.mesh.num_face_vertices[f];
                    for(size_t v=0; v<fv; v++){
                        const auto &idx = s.mesh.indices[idx_offset+v];
                        int vi = idx.vertex_index;
                        int ni = idx.normal_index;
                        if(vi >= 0 && ni >= 0){
                            Vec3 n(attrib.normals[3*ni+0], attrib.normals[3*ni+1], attrib.normals[3*ni+2]);
                            VN[vi] += n;
                            VNcount[vi]++;
                        }
                    }
                    idx_offset += fv;
                }
            }
            for(size_t i=0;i<numVerts;i++) if(VNcount[i]>0) VN[i] = normalize(VN[i]);
        } else {
            // Direct mapping (may be wrong if different indexing)
            for(size_t i=0;i<numVerts && (3*i+2)<attrib.normals.size();i++){
                VN[i] = normalize(Vec3(attrib.normals[3*i+0], attrib.normals[3*i+1], attrib.normals[3*i+2]));
                VNcount[i] = 1;
            }
        }
    }

    // If still missing normals, compute per-face and average to vertices
    if(!hasVN){
        for(const auto& s : shapes){
            size_t idx_offset = 0;
            for(size_t f=0; f < s.mesh.num_face_vertices.size(); f++){
                unsigned char fv = s.mesh.num_face_vertices[f];
                if(fv < 3){ idx_offset += fv; continue; }
                // Fan triangulation for polygon (v0, v1, v2), (v0, v2, v3), ...
                const auto &idx0 = s.mesh.indices[idx_offset+0];
                Vec3 v0 = V[idx0.vertex_index];
                for(size_t v=1; v+1<fv; v++){
                    const auto &idx1 = s.mesh.indices[idx_offset+v];
                    const auto &idx2 = s.mesh.indices[idx_offset+v+1];
                    Vec3 v1 = V[idx1.vertex_index];
                    Vec3 v2 = V[idx2.vertex_index];
                    Vec3 fn = normalize(cross(v1 - v0, v2 - v0));
                    VN[idx0.vertex_index] += fn; VNcount[idx0.vertex_index]++;
                    VN[idx1.vertex_index] += fn; VNcount[idx1.vertex_index]++;
                    VN[idx2.vertex_index] += fn; VNcount[idx2.vertex_index]++;
                }
                idx_offset += fv;
            }
        }
        for(size_t i=0;i<numVerts;i++) if(VNcount[i]>0) VN[i] = normalize(VN[i]);
        hasVN = true;
    }

    // Write ASCII PCD
    std::ofstream ofs(output);
    if(!ofs){ std::cerr << "Cannot open output: " << output << "\n"; return 4; }
    ofs << "# .PCD v0.7 - Point Cloud Data file format\n";
    ofs << "VERSION 0.7\n";
    ofs << "FIELDS x y z normal_x normal_y normal_z\n";
    ofs << "SIZE 4 4 4 4 4 4\n";
    ofs << "TYPE F F F F F F\n";
    ofs << "COUNT 1 1 1 1 1 1\n";
    ofs << "WIDTH " << numVerts << "\n";
    ofs << "HEIGHT 1\n";
    ofs << "VIEWPOINT 0 0 0 1 0 0 0\n";
    ofs << "POINTS " << numVerts << "\n";
    ofs << "DATA ascii\n";
    for(size_t i=0;i<numVerts;i++){
        Vec3 n = (VNcount[i]>0) ? VN[i] : Vec3(0,0,1);
        ofs << static_cast<float>(V[i].x) << ' ' << static_cast<float>(V[i].y) << ' ' << static_cast<float>(V[i].z) << ' '
            << static_cast<float>(n.x) << ' ' << static_cast<float>(n.y) << ' ' << static_cast<float>(n.z) << "\n";
    }
    ofs.close();
    std::cout << "Wrote PCD: " << output << " (" << numVerts << " points)\n";
    return 0;
}
