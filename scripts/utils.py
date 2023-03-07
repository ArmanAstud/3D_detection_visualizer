import numpy as np
import os, sys
import pandas as pd

import dash
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

def return_vertex(df, grid_x_min, grid_x_max, grid_y_min, grid_y_max):
	all_vertex = []
	all_labels = []
	for i in range(len(df)):
		id_box	 = df['id'][i]
		
		x_center = df['x'][i]
		y_center = df['y'][i]
		z_center = df['z'][i]

		w_half 	= df['w'][i] / 2
		l_half 	= df['l'][i] / 2
		h 		= df['h'][i]
		
		# Construir vertices 
		x_min = x_center - l_half
		y_min = y_center - w_half
		z_min = z_center
		x_max = x_center + l_half
		y_max = y_center + w_half
		z_max = z_center + h

		if x_min<grid_x_min or x_max>grid_x_max or y_min<grid_y_min or y_max>grid_y_max: continue
		
		vertices = np.array([
			[x_min, y_min, z_min],
			[x_max, y_min, z_min],
			[x_max, y_max, z_min],
			[x_min, y_max, z_min],

			[x_min, y_min, z_max],
			[x_max, y_min, z_max],
			[x_max, y_max, z_max],
			[x_min, y_max, z_max]
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
		all_labels.append('Car: {}'.format(id_box))

	return all_vertex, all_labels

def draw_frame(data_dir, frame_list, frame, fig, grid_x_min, grid_x_max, grid_y_min, grid_y_max):

	df = pd.read_csv(os.path.join(data_dir, frame_list[frame]), delimiter=' ')

	# Calcular los vertices de la caja
	all_vertex, all_labels = return_vertex(df, grid_x_min, grid_x_max, grid_y_min, grid_y_max)
	for i, _ in enumerate(all_vertex):
		vertices = all_vertex[i]
		label = all_labels[i]
		
		faces = go.Mesh3d(
			x=vertices[:, 0],
			y=vertices[:, 1],
			z=vertices[:, 2],
			#i=indices[:, 0],
			#j=indices[:, 1],
			#k=indices[:, 2],
			i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
			j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
			k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
			name=label
		)
		fig.add_trace(faces)

	return fig