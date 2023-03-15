import numpy as np
import os, sys, math
import pandas as pd

import dash
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output

import plotly.graph_objs as go


class Obstacle():
	def __init__(self, df, dataset, frame_name):
		self.df = df
		self.coordinate_system = dataset.coordinate_system

		if 'id' in df.keys():
			self.id = df['id']
		else:
			self.id = -1.

		if self.coordinate_system == 'camera_coordinate_system':
			self.x_center, self.y_center, self.z_center, self.yaw = dataset.project_center_camera_to_lidar(frame_name, df['x'], df['y'], df['z'], df['yaw'])

		elif self.coordinate_system == 'lidar_coordinate_system':
			self.x_center	= df['x']
			self.y_center	= df['y']
			self.z_center	= df['z']
			self.yaw		= df['yaw']
		else:
			print("Coordinate System: {} NOT implemented!".format(self.coordinate_system))
			sys.exit(1)
		self.w 	= df['w']
		self.l 	= df['l']
		self.h 	= df['h']

		if 'score' in df.keys():
			self.score = df['score']
		else:
			self.score = -1.

		self.label = df['label']

	def print_obstacle(self):
		print('------')
		print(self.df)
		print('------\n')
		
################################ 3D BOXES ################################
def return_vertex(df, dataset, frame_name):
	all_vertex = []
	all_labels = []
	all_obstacles = []

	for i in range(len(df)):
		# Parser obstacle
		obstacle = Obstacle(df.iloc[int(i)], dataset, frame_name)
		#obstacle.print_obstacle()

		id_box	 = int(obstacle.id)
		x_center = obstacle.x_center
		y_center = obstacle.y_center
		z_center = obstacle.z_center
		yaw		 = obstacle.yaw
		w_half 	= obstacle.w / 2.
		l_half 	= obstacle.l / 2.
		h		= obstacle.h

		# Construir vertices 
		point_A_x = (x_center - l_half * math.cos(-yaw) - w_half  * math.sin(-yaw))
		point_A_y = (y_center + l_half * math.sin(-yaw) - w_half  * math.cos(-yaw))

		# Get B point
		point_B_x = (x_center + l_half* math.cos(-yaw) - w_half  * math.sin(-yaw))
		point_B_y = (y_center - l_half* math.sin(-yaw) - w_half  * math.cos(-yaw))

		# Get C point
		point_C_x = (x_center + l_half * math.cos(-yaw) + w_half  * math.sin(-yaw))
		point_C_y = (y_center - l_half * math.sin(-yaw) + w_half  * math.cos(-yaw))

		# Get D point
		point_D_x = (x_center - l_half * math.cos(-yaw) + w_half  * math.sin(-yaw))
		point_D_y = (y_center + l_half * math.sin(-yaw) + w_half  * math.cos(-yaw))
		
		vertices = np.array([
			[point_A_x, point_A_y, z_center],
			[point_B_x, point_B_y, z_center],
			[point_C_x, point_C_y, z_center],
			[point_D_x, point_D_y, z_center],

			[point_A_x, point_A_y, z_center+h],
			[point_B_x, point_B_y, z_center+h],
			[point_C_x, point_C_y, z_center+h],
			[point_D_x, point_D_y, z_center+h]
		])
		indices = np.array([
			[0, 1, 2, 3],
			[0, 1, 5, 4],
			[1, 2, 6, 5],
			[2, 3, 7, 6],
			[3, 0, 4, 7],
			[4, 5, 6, 7]
		])

		all_vertex.append(vertices)
		all_labels.append('{}-{}: {:.3f}'.format(obstacle.label, id_box, obstacle.score))

	return all_vertex, all_labels

def draw_annotations_frame(dataset, frame_list, frame, fig):

	if frame_list is None: return fig

	df = pd.read_csv(os.path.join(dataset.annotations_data_path, frame_list[frame]), delimiter=' ', names=dataset.annotations_format)

	# Calcular los vertices de la caja
	all_vertex, all_labels = return_vertex(df, dataset, frame_list[frame])
	for i, _ in enumerate(all_vertex):
		vertices = all_vertex[i]
		label = all_labels[i]
		
		faces = go.Mesh3d(
			x=vertices[:, 0],
			y=vertices[:, 1],
			z=vertices[:, 2],
			i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
			j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
			k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
			name=label,
			opacity=0.3
		)
		fig.add_trace(faces)

	return fig

################################ LiDAR ################################
def draw_lidar(dataset, lidar_frame_list, frame, lidar_res):
	
	filename = os.path.join(dataset.lidar_data_path, lidar_frame_list[frame])
	points = dataset.load_lidar(filename)

	PC_scatter = go.Scatter3d(
		x=points["x"],
		y=points["y"],
		z=points["z"],
		mode='markers',
		marker=dict(
			size=lidar_res,
			color=[0,0,0],
			opacity=0.3
		)
	)

	return PC_scatter