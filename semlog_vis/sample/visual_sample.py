import sys, os
sys.path.append("..")

from semlog_vis.PointCloudGenerator import PointCloudGenerator

rgb='p.png'
depth='d.png'
pc='pc.ply'


a = PointCloudGenerator(rgb, depth, pc,
                          focal_length=320, scalingfactor=10)
a.calculate()
a.write_ply()
a.show_point_cloud()
a.save_npy()