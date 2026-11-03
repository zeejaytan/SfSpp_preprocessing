#!/usr/bin/env python3
"""patch_attitude67.py SRC DST -- ticket 67 task 3: instrumented COPY of the guarded shim (G.cpp).

Adds, before PairwisePruning, a verbatim replay of PairwisePruning's first loop
(class/feature_matching.cpp:1637-1707: Icp, trans_ update, axis angle, OverlapCheck_3d(..., 50.0))
on a copy of the candidate list, and writes Result/T67_candidates.tsv with one row per LCS candidate.
Writes Result/T67_gtpairs.tsv: every GT-adjacent pair posed at the GT relative pose.
After PairwisePruning, writes Result/T67_survivors.tsv. The real pruning and everything after it
run unchanged; the replay touches only copies.

Pose convention follows CountResult (class/data_structure.cpp:1001-1009): relative pose of j in i is
T_i^-1 * T_j, estimate T_result = Input(C) on T_axis (Trans::Input left-multiplies, :555-564), so a
candidate C (moving m -> fixed f, both in their axis frames) gives est = A_f^-1 * C * A_m and the GT
pose in the axis frames is C_gt = A_f * (G_f^-1 * G_m) * A_m^-1.
Each anchor must occur exactly once, or the patch refuses (exit 2).
"""
import sys

src, dst = sys.argv[1], sys.argv[2]
text = open(src).read()

PRE = r'''	{
		// T67 instrument (ticket 67 task 3) -- replay of PairwisePruning's first loop on copies.
		const double T67_PI = 3.14159265358979;
		auto t67_resid = [&](const Matrix4d& C, int f, int m, double& med, int& ncontact) {
			const MatrixXd& Pf = shard[f].edge_line_.point_;
			const MatrixXd& Pm = shard[m].edge_line_.point_;
			vector<double> d;
			ncontact = 0;
			for (int a = 0; a < Pm.cols(); a++) {
				Vector3d q = C.block<3, 3>(0, 0) * Vector3d(Pm(0, a), Pm(1, a), Pm(2, a)) + C.block<3, 1>(0, 3);
				double best = 1e30;
				for (int b = 0; b < Pf.cols(); b++) {
					double dd = (q - Vector3d(Pf(0, b), Pf(1, b), Pf(2, b))).norm();
					if (dd < best) best = dd;
				}
				d.push_back(best);
				if (best < 2.0) ncontact++;
			}
			sort(d.begin(), d.end());
			med = d.empty() ? -1 : d[d.size() / 2];
		};
		auto t67_gt_axis = [&](int f, int m, Matrix4d& Cgt, Matrix4d& gt) {
			Matrix4d A_f, A_m_inv, G_f_inv, G_m;
			T_axis[f].Output(A_f);
			T_axis[m].InvOut(A_m_inv);
			GT_trans[f].InvOut(G_f_inv);
			GT_trans[m].Output(G_m);
			gt = G_f_inv * G_m;
			Cgt = A_f * gt * A_m_inv;
		};
		auto t67_axdeg = [&](const Matrix3d& R, int f, int ax_f, int m, int ax_m) {
			Vector3d an = R * shard[m].edge_line_.axis_norm_[ax_m];
			double dv = an.dot(shard[f].edge_line_.axis_norm_[ax_f]);
			dv = max(-1.0, min(1.0, dv));
			return acos(dv) * 180.0 / T67_PI;
		};

		ofstream t67g(path + "Result/T67_gtpairs.tsv");
		t67g << "fix\tmov\tdots_fix\tdots_mov\tn_axis_fix\tn_axis_mov\tgt_axis_unfold_deg\tgt_join_median_mm\tgt_contact_lt2mm" << endl;
		for (int f = 0; f < SHARD_NUMBER; f++) {
			for (int m = f + 1; m < SHARD_NUMBER; m++) {
				if (!GT_graph(f, m) || !shard[f].is_matching_ || !shard[m].is_matching_) continue;
				Matrix4d Cgt, gt;
				t67_gt_axis(f, m, Cgt, gt);
				double med; int nc;
				t67_resid(Cgt, f, m, med, nc);
				t67g << f + 1 << "\t" << m + 1 << "\t" << shard[f].edge_line_.point_.cols() << "\t" << shard[m].edge_line_.point_.cols()
					<< "\t" << shard[f].edge_line_.axis_norm_.size() << "\t" << shard[m].edge_line_.axis_norm_.size()
					<< "\t" << t67_axdeg(Cgt.block<3, 3>(0, 0), f, 0, m, 0) << "\t" << med << "\t" << nc << endl;
			}
		}
		t67g.close();

		ofstream t67(path + "Result/T67_candidates.tsv");
		t67 << "idx\tfix\tmov\tgt_edge\tsize\tstart_x\tend_x\tstart_y\tend_y\taxis_x\taxis_y\tscore\tinlier\taxis_fold_deg\taxis_unfold_deg\toverlap\tarea\trot_err_deg\ttrans_err_cr_mm\tcentroid_err_mm\tjoin_median_mm\tcontact_lt2mm\tgt_axis_unfold_deg" << endl;
		vector<BreakLine> L(SHARD_NUMBER);
		for (int i = 0; i < SHARD_NUMBER; i++) L[i] = shard[i].edge_line_;
		vector<LCSIndex> lcsout;
		for (list<LCSIndex>::iterator it = LCS_out.begin(); it != LCS_out.end(); ++it) {
			LCSIndex c = *it;
			lcsout.push_back(c);
			CycleNode cycle;
			cycle.edges.push_back(lcsout.size() - 1);
			cycle.nodes.push_back(c.shard_y_);
			cycle.nodes.push_back(c.shard_x_);
			vector<Matrix3d> R_p(SHARD_NUMBER, Matrix3d::Identity());
			vector<Vector3d> t_p(SHARD_NUMBER, Vector3d(0, 0, 0));
			Icp(L, R_p, t_p, lcsout, cycle, true, true);
			int f = c.shard_y_ - 1, m = c.shard_x_ - 1;
			Matrix3d R_fix_i_1 = R_p[f].inverse();
			Vector3d t_fix_i_1 = -R_fix_i_1 * t_p[f];
			c.trans_.Set(R_p[m], t_p[m], m + 1, f + 1);
			c.trans_.Input(R_fix_i_1, t_fix_i_1);
			Matrix3d R_c; Vector3d t_c;
			c.trans_.Output(R_c, t_c);
			Vector3d amn = R_c * L[m].axis_norm_[c.axis_index_x_];
			double dv = max(-1.0, min(1.0, amn.dot(L[f].axis_norm_[c.axis_index_y_])));
			double unfold = acos(dv);
			double fold = min(unfold, 3.14159 - unfold);
			EdgeLineMove(L[f], R_fix_i_1, t_fix_i_1);
			EdgeLineMove(L[m], R_fix_i_1, t_fix_i_1);
			double area(0), length(0);
			bool overlap = OverlapCheck_3d(L[f], L[m], area, length, 50.0);
			Matrix3d R_re; Vector3d t_re;
			c.trans_.InvOut(R_re, t_re);
			EdgeLineMove(L[m], R_re, t_re);

			Matrix4d C = Matrix4d::Identity();
			C.block<3, 3>(0, 0) = R_c;
			C.block<3, 1>(0, 3) = t_c;
			Matrix4d Cgt, gt, A_f_inv, A_m, A_m_inv;
			t67_gt_axis(f, m, Cgt, gt);
			T_axis[f].InvOut(A_f_inv);
			T_axis[m].Output(A_m);
			T_axis[m].InvOut(A_m_inv);
			Matrix4d est = A_f_inv * C * A_m;
			Matrix4d E = gt * est.inverse();
			double rot_err = AngleAxisd(Matrix3d(E.block<3, 3>(0, 0))).angle() * 180.0 / T67_PI;
			double tr_cr = E.block<3, 1>(0, 3).norm();
			Vector3d qc = shard[m].edge_line_.point_.rowwise().mean();
			Vector4d pc = A_m_inv * Vector4d(qc[0], qc[1], qc[2], 1.0);
			double cen_err = ((gt - est) * pc).head<3>().norm();
			double med; int nc;
			t67_resid(C, f, m, med, nc);
			t67 << it->index_ << "\t" << f + 1 << "\t" << m + 1 << "\t" << (GT_graph(f, m) ? 1 : 0) << "\t" << c.size_
				<< "\t" << c.start_.x << "\t" << c.end_.x << "\t" << c.start_.y << "\t" << c.end_.y
				<< "\t" << c.axis_index_x_ << "\t" << c.axis_index_y_ << "\t" << cycle.score << "\t" << cycle.inlier
				<< "\t" << fold * 180.0 / T67_PI << "\t" << unfold * 180.0 / T67_PI << "\t" << (overlap ? 1 : 0) << "\t" << area
				<< "\t" << rot_err << "\t" << tr_cr << "\t" << cen_err << "\t" << med << "\t" << nc
				<< "\t" << t67_axdeg(Cgt.block<3, 3>(0, 0), f, c.axis_index_y_, m, c.axis_index_x_) << endl;
		}
		t67.close();
		cout << "T67-INSTRUMENT candidates=" << LCS_out.size() << " written" << endl;
	}
'''

POST = r'''	{
		ofstream t67s(path + "Result/T67_survivors.tsv");
		t67s << "idx\tfix\tmov\tscore\tinlier\taxis_fold_deg\toverlap" << endl;
		for (list<LCSIndex>::iterator it = LCS_out.begin(); it != LCS_out.end(); ++it)
			t67s << it->index_ << "\t" << it->shard_y_ << "\t" << it->shard_x_ << "\t" << it->score_ << "\t" << it->inliner_
				<< "\t" << it->axis_angle_ * 180.0 / 3.14159265358979 << "\t" << (it->overlap_ ? 1 : 0) << endl;
	}
'''

PRE_ANCHOR = '\tPairwisePruning(shard, LCS_out);\n'
POST_ANCHOR = '\tcout << "Total number pruned : " << LCS_out.size() << endl;\n'

for anchor in (PRE_ANCHOR, POST_ANCHOR):
    n = text.count(anchor)
    if n != 1:
        sys.stderr.write('anchor count %d (want 1): %r\n' % (n, anchor))
        sys.exit(2)
text = text.replace(PRE_ANCHOR, PRE + PRE_ANCHOR)
text = text.replace(POST_ANCHOR, POST_ANCHOR + POST)
open(dst, 'w', newline='\n').write(text)
print('ATTITUDE OK', dst)
