import numpy as np
import json
import os, sys
import projection_utils_Kraw

class KittiDataset():
	def __init__(self, args):
		self.cfg_filename = args.dataset_cfg
		self.cfg_json = json.load(open(self.cfg_filename))
		
		#Annotations
		if "annotations" in self.cfg_json.keys():
			self.annotations_data_path = self.cfg_json["annotations"]["annotations_data_path"]
			self.annotations_format = self.cfg_json["annotations"]["annotations_format"].replace("\n","").split()
			self.coordinate_system = self.cfg_json["annotations"]["coordinate_system"]
			self.annotations_frame_list = os.listdir(self.annotations_data_path)
			self.annotations_frame_list.sort()

		#LiDAR
		if "lidar" in self.cfg_json.keys():
			self.lidar_data_path = self.cfg_json["lidar"]["lidar_data_path"]
			self.lidar_frame_list = os.listdir(self.lidar_data_path)
			self.lidar_frame_list.sort()

		#Calibs
		self.calibration_path = self.cfg_json["calibs"]["calibs_path"]
			
	def project_center_camera_to_lidar(self,frame_name, x, y, z, yaw):
		k = projection_utils_Kraw.Calibration(os.path.join(self.calibration_path,frame_name) )
		x, y, z = k.project_rect_to_velo( [[x,y,z]] )[0]
		# increase Z of all points -> height of the Sensor
		z += 1.73
		#rot_y -> yaw
		yaw = -(yaw+np.pi/2)
		return x,y,z, yaw

	def load_lidar(self, filename):
		dt = np.dtype([('x', '<f4'), ('y', '<f4'), ('z', '<f4'), ('i', '<f4')])
		points = np.fromfile(filename, dtype=dt)

		# increase Z of all points -> height of the Sensor
		points["z"] += 1.73
		return points
