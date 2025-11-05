#ifndef DATA_PATH_H
#define DATA_PATH_H

// Pot 선택: 하나만 정의되어야 함
#define POT_A
//#define POT_B
//#define POT_C
//#define POT_D
//#define POT_E
//#define POT_F
//#define POT_G
//#define POT_H
//#define POT_I
//#define POT_J

#include <string>
#include <cstdlib>  // For getenv
#include <cstring>  // For strlen

//############################################ Pot ID (MeshProcessing & EdgelineExtraction) ############################################//
#ifdef POT_A
    static const std::string potID = "A";
#elif defined(POT_B)
    static const std::string potID = "B";
#elif defined(POT_C)
    static const std::string potID = "C";
#elif defined(POT_D)
    static const std::string potID = "D";
#elif defined(POT_E)
    static const std::string potID = "E";
#elif defined(POT_F)
    static const std::string potID = "F";
#elif defined(POT_G)
    static const std::string potID = "G";
#elif defined(POT_H)
    static const std::string potID = "H";
#elif defined(POT_I)
    static const std::string potID = "I";
#elif defined(POT_J)
    static const std::string potID = "J";
#else
    #error "No POT defined! Please define one POT (e.g., POT_A)."
#endif

// Runtime pot naming support via environment variable
inline std::string getPotNameFromEnv() {
    const char* envPotName = std::getenv("POT_NAME");
    if (envPotName != nullptr && std::strlen(envPotName) > 0) {
        return std::string(envPotName);
    }
    // Fallback to compiled default
    return "Pot_" + potID;
}

inline std::string getMeshDatasetPath(const std::string& potID) {
    std::string potName = getPotNameFromEnv();
    return "Dataset/Mesh/" + potName + "/";  // Runtime pot naming support
}

inline std::string getPointDatasetPath(const std::string& potID) {
    std::string potName = getPotNameFromEnv();
    return "Dataset/Point/" + potName + "/";  // Runtime pot naming support
}

inline std::string getBreaklineDatasetPath(const std::string& potID) {
    std::string potName = getPotNameFromEnv();
    // Check if we should use SfS_pp structure for direct output
    const char* outputBase = std::getenv("NURBS_OUTPUT_BASE");
    if (outputBase != nullptr && std::strlen(outputBase) > 0) {
        return std::string(outputBase) + "/SfS_pp/Breaklines/";
    }
    return "Dataset/Breaklines/" + potName + "/";  // Runtime pot naming support
}

inline std::string getSurfaceDatasetPath(const std::string& potID) {
    std::string potName = getPotNameFromEnv();
    return "Dataset/Surfaces/" + potName + "/";  // Runtime pot naming support
}

inline std::string tempPath() {
    return "Temp/";  // Changed for container compatibility - no ../ needed since we're in workspace
}

inline std::string tempEdgePath(const std::string& potID) {
    std::string potName = getPotNameFromEnv();
    return "Temp/Temp_edge/" + potName + "/";  // Runtime pot naming support
}

inline std::string tempDataPath(const std::string& potID) {
    std::string potName = getPotNameFromEnv();
    // Check if we should use SfS_pp structure for direct output
    const char* outputBase = std::getenv("NURBS_OUTPUT_BASE");
    if (outputBase != nullptr && std::strlen(outputBase) > 0) {
        return std::string(outputBase) + "/SfS_pp/Surfaces/";
    }
    return "Temp/Data/" + potName + "/";  // Runtime pot naming support
}

inline std::string tempIntermediatePath(const std::string& potID) {
    std::string potName = getPotNameFromEnv();
    return "Temp/Temp/" + potName + "/";  // Runtime pot naming support
}

#endif // DATA_PATH_H
