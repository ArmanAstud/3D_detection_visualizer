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
	def __init__(self, df):
		self.df = df

		self.id = df['id']
		
		self.x_center	= df['x']
		self.y_center	= df['y']
		self.z_center	= df['z']
		self.yaw		= df['yaw']

		self.w 	= df['w']
		self.l 	= df['l']
		self.h 	= df['h']

		self.score = df['score']
		self.label = df['label']

	def print_obstacle(self):
		print('------')
		print(self.df)
		print('------\n')
		

def return_vertex(df, grid_x_min, grid_x_max, grid_y_min, grid_y_max):
	all_vertex = []
	all_labels = []
	all_obstacles = []
	#print(df)
	for i in range(len(df)):
		# Parser obstacle
		obstacle = Obstacle(df.iloc[int(i)])
		obstacle.print_obstacle()

		id_box	 = obstacle.id
		x_center = obstacle.x_center
		y_center = obstacle.y_center
		z_center = obstacle.z_center
		yaw		 = obstacle.yaw
		w_half 	= obstacle.w / 2
		l_half 	= obstacle.l / 2
		h 		= obstacle.h

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
		all_labels.append('{}-{}: {:.3f}'.format(df['label'][i], id_box, df['score'][i]))

	return all_vertex, all_labels

def draw_annotations_frame(data_dir, annots_format, frame_list, frame, fig, grid_x_min, grid_x_max, grid_y_min, grid_y_max):

	if frame_list is None: return fig

	df = pd.read_csv(os.path.join(data_dir, frame_list[frame]), delimiter=' ', names=annots_format)

	# Calcular los vertices de la caja
	all_vertex, all_labels = return_vertex(df, grid_x_min, grid_x_max, grid_y_min, grid_y_max)
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
			name=label
		)
		fig.add_trace(faces)

	return fig