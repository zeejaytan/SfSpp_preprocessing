        // SFS-P174 (pota-repro ticket 174): rim-strip reclaim.
        // Region growing at 4.5deg stops at the rim fold and strands the
        // 2-6mm rim strip in the unclustered pile (pota-repro 172: strip
        // sits 1.1-5.3mm off the sheet), while loosening the threshold
        // merges the two faces before the rim is reached (174 sweep: at
        // 8deg 99.9% of face 2 is absorbed into Surface_0; at 20deg no
        // split survives). Reclaim keeps every cluster label (faces stay
        // separate by construction -- a free point only JOINS its nearest
        // cluster, clusters never merge) and absorbs spatially adjacent,
        // normal-compatible free points, iterating to convergence so the
        // strip chains outward to the true rim. Laptop prototype on staged
        // C01 (D=6mm, A=60deg): rim reach 7/188 -> 188/188 stations <2mm
        // with faces still distinct (med separation 13.7mm). ORIG-free:
        // pure geometry, no ORIG constants. Env: SFS_RECLAIM_D mm
        // (default 6.0; <=0 disables, restoring pre-174 behavior),
        // SFS_RECLAIM_A deg (default 60.0).
        {
            double p174_D = 6.0, p174_A = 60.0;
            if (const char* p174_e = std::getenv("SFS_RECLAIM_D")) p174_D = std::atof(p174_e);
            if (const char* p174_e = std::getenv("SFS_RECLAIM_A")) p174_A = std::atof(p174_e);
            if (p174_D > 0.0 && clusters.size() > 1)
            {
                const double p174_cos = std::cos(p174_A * M_PI / 180.0);
                const int p174_N = static_cast<int>(cloud->points.size());
                std::vector<int> p174_owner(p174_N, -1);
                for (size_t p174_c = 0; p174_c < clusters.size(); ++p174_c)
                    for (int p174_idx : clusters[p174_c].indices)
                        if (p174_idx >= 0 && p174_idx < p174_N) p174_owner[p174_idx] = static_cast<int>(p174_c);
                int p174_admit0 = 0, p174_admit1 = 0;
                for (int p174_rnd = 0; p174_rnd < 12; ++p174_rnd)
                {
                    pcl::PointCloud<pcl::PointXYZ>::Ptr p174_mem(new pcl::PointCloud<pcl::PointXYZ>);
                    std::vector<int> p174_memIdx;
                    p174_mem->points.reserve(p174_N);
                    for (int p174_i = 0; p174_i < p174_N; ++p174_i)
                        if (p174_owner[p174_i] >= 0) { p174_mem->points.push_back(cloud->points[p174_i]); p174_memIdx.push_back(p174_i); }
                    if (p174_mem->points.empty()) break;
                    pcl::KdTreeFLANN<pcl::PointXYZ> p174_tree;
                    p174_tree.setInputCloud(p174_mem);
                    std::vector<int> p174_take;
                    std::vector<int> p174_takeOwner;
                    for (int p174_i = 0; p174_i < p174_N; ++p174_i)
                    {
                        if (p174_owner[p174_i] >= 0) continue;
                        std::vector<int> p174_k(1); std::vector<float> p174_d(1);
                        if (p174_tree.nearestKSearch(cloud->points[p174_i], 1, p174_k, p174_d) < 1) continue;
                        if (p174_d[0] > p174_D * p174_D) continue;
                        const int p174_src = p174_memIdx[p174_k[0]];
                        const pcl::Normal& p174_nf = normals->points[p174_i];
                        const pcl::Normal& p174_ns = normals->points[p174_src];
                        const double p174_lf = std::sqrt(p174_nf.normal_x * p174_nf.normal_x + p174_nf.normal_y * p174_nf.normal_y + p174_nf.normal_z * p174_nf.normal_z);
                        const double p174_ls = std::sqrt(p174_ns.normal_x * p174_ns.normal_x + p174_ns.normal_y * p174_ns.normal_y + p174_ns.normal_z * p174_ns.normal_z);
                        if (p174_lf < 1e-9 || p174_ls < 1e-9) continue;
                        const double p174_dot = (p174_nf.normal_x * p174_ns.normal_x + p174_nf.normal_y * p174_ns.normal_y + p174_nf.normal_z * p174_ns.normal_z) / (p174_lf * p174_ls);
                        if (p174_dot < p174_cos) continue;
                        p174_take.push_back(p174_i);
                        p174_takeOwner.push_back(p174_owner[p174_src]);
                    }
                    if (p174_take.empty()) break;
                    for (size_t p174_k2 = 0; p174_k2 < p174_take.size(); ++p174_k2)
                    {
                        const int p174_c = p174_takeOwner[p174_k2];
                        clusters[p174_c].indices.push_back(p174_take[p174_k2]);
                        p174_owner[p174_take[p174_k2]] = p174_c;
                        if (p174_c == 0) ++p174_admit0; else if (p174_c == 1) ++p174_admit1;
                    }
                }
                std::sort(clusters.begin(), clusters.end(), myobject3);
                std::cout << "[SFS-P174] rim reclaim D=" << p174_D << "mm A=" << p174_A << "deg: +" << p174_admit0 << " to clusters[0], +" << p174_admit1 << " to clusters[1]" << std::endl;
            }
        }

