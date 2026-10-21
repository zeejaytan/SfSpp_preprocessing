src = open('C:/PR/SfSpp_preprocessing/.scratch/pota234/mesh_processing_headless.cpp','rb').read().replace(b'\r\n',b'\n').decode('utf-8',errors='surrogateescape')
i = src.index('// TICKET 234 PAPER ARM')
j = src.index('void surfaceSegmentation(std::string filePath, int minCluster')
block = src[i:j]
heads = [
 '#include <vector>', '#include <algorithm>', '#include <cmath>',
 '#include <fstream>', '#include <string>', '#include <Eigen/Dense>',
 '#include <Eigen/Core>', '#include <pcl/point_types.h>',
 '#include <pcl/point_cloud.h>', '#include <pcl/kdtree/kdtree_flann.h>',
 '#include <pcl/common/common.h>', '#include <pcl/segmentation/region_growing.h>',
 'bool myobject3(const pcl::PointIndices &a, const pcl::PointIndices &b){return a.indices.size()>b.indices.size();}',
]
open('C:/PR/SfSpp_preprocessing/.scratch/pota234/probe234b.cpp','w').write('\n'.join(heads) + '\n' + block + 'int main(){return 0;}\n')
print('probe bytes:', len(block))
