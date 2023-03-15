# Copyright (C) 2023 Armando Astudillo

import os, sys
import numpy as np
import pandas as pd

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State	

import plotly.graph_objs as go
import dash_daq as daq

import utils
import datasets

import argparse

def str_to_bool(value):
	if value.lower() in {'false', 'f', '0', 'no', 'n'}:
		return False
	elif value.lower() in {'true', 't', '1', 'yes', 'y'}:
		return True

parser = argparse.ArgumentParser(description='3D_detection_visualizer.', fromfile_prefix_chars='@')

# Annotations
parser.add_argument('--dataset',			type=str,			help='flag to read annotations',			default="KITTI")
parser.add_argument('--dataset_cfg',		type=str,			help='path were dataset config is stored',	default="cfg/kitti_dataset.json")

# Annotations
parser.add_argument('--annotations',		type=str_to_bool,	help='flag to read annotations',			default="True")

# PointCloud
parser.add_argument('--lidar',				type=str_to_bool,	help='flag to read lidar pointcloud',		default="False")
parser.add_argument('--lidar_res',			type=float,			help='float value for lidar_res',			default=0.3)

# Grid Config
parser.add_argument('--grid_res',	type=float,	help='float value for grid_res',	default=1.0)
parser.add_argument('--grid_size',	type=float,	help='float value for grid_size',	default=50.0)


args = parser.parse_args()

#-------------------------------------------------------------------------------------------------
# Crear la app de Dash
app = dash.Dash()
frame = 0
frame_list = None
lidar_frame_list = None
first_time = 0

# Dataset
dataset_dict = {"KITTI": datasets.KittiDataset(args)}
dataset = dataset_dict[args.dataset]

# Annotations
if args.annotations:
	## Frame list
	frame_list = dataset.annotations_frame_list

#  LiDAR
if args.lidar:
	## Frame list
	lidar_frame_list = dataset.lidar_frame_list

# Definir los params del grid
grid_res = args.grid_res # metros por cuadrado
grid_size = args.grid_size # metros por cuadrado
grid_x_min = -grid_size # coordenada x min del grid
grid_x_max = grid_size # coordenada x max del grid
grid_y_min = -grid_size # coordenada y min del grid
grid_y_max = grid_size # coordenada y max del grid
grid_z_min = 0. # coordenada y min del grid
grid_z_max = grid_size # coordenada y max del grid



# Crear la figura
fig = go.Figure()
init_cam = fig.layout.scene
# draw first annotation
if args.annotations:
	fig = utils.draw_annotations_frame(dataset, frame_list, frame, fig)

# draw first pointCloud
if args.lidar:
	fig.add_trace(utils.draw_lidar(dataset, lidar_frame_list, frame, args.lidar_res))

# Dibujar el grid
grid = go.Scatter3d(
	x=np.arange(grid_x_min, grid_x_max, grid_res),
	y=np.arange(grid_y_min, grid_y_max, grid_res),
	z=np.arange(grid_z_min, grid_z_max, grid_res),
	mode='markers',
	marker=dict(size=1, color='black')
)

camera = dict(
	up=dict(x=0, y=0, z=1),
	center=dict(x=0, y=0, z=0),
	eye=dict(x=-1.25, y=0, z=2)
)
fig.update_layout(scene_camera=camera)


#-------------------------------------------------------------------------------------------------
# Definir el diseño de la aplicación
app.layout = html.Div(children=
	[
		# titulo
		html.H1(children='Visualization tool for 3D detecion pipeline'),
		
		# First container: world with 3D bboxes
		html.Div
		([
	
			html.H2(children='Visualización de cajas 3D'),

			# Div vertical con botonera
			html.Div(
				style={
					'display': 'flex',
					'flex-direction': 'row',
					'flex': '1',
					'margin': 'auto%'
				},
				children=[
				daq.ToggleSwitch(
						id='lidar-switch',
						value=False,
						label='Draw LiDAR PointCloud',
						labelPosition='top',
						style={'width': "10%"}
					),
				daq.ToggleSwitch(
						id='annotations-switch',
						value=True,
						label='Draw Annotations',
						labelPosition='top',
						style={'width': "10%"}
					),

				]
			),

			# Div Vertical con Visualizador de cajas y slider de grid size
			html.Div
			(
				style={'width': '50%', 'margin': 'auto', 'display': 'flex'},
				children=[
				# 3D principal
				dcc.Graph
				(
					id='cajas-3d',
					figure=fig,
					style={'width': '90vh', 'height': '90vh'},
					config={'responsive': False},
				),

				# Slider vertical con escala del grafico
				html.Div(
					style={
						'display': 'flex',
						'flex-direction': 'column',
						'flex': '1',
						'margin': 'auto'
					},
					children=[
					html.Label('Tamaño del grid (metros)'),
					dcc.Slider(
						id='slider-grid-size',
						min=10,
						max=100,
						step=10,
						value=50,
						marks={size: str(size) for size in [10, 30, 50, 70, 90, 100]},
						vertical=True
					),]
				)
				]
			), 

			# Div Horizontal con slider de tiempo
			html.Div
			([
				html.Label('Frame'),
				dcc.Slider(
					id='slider-frame',
					min=0,
					max=len(frame_list)-1,
					step=1,
					value=0,
					marks={size: str(size) for size in np.arange(0, len(frame_list), 1).tolist()}
				)
			], 
			style={'width': '50%', 'margin': 'auto'}
			)
		])
])


#-------------------------------------------------------------------------------------------------
# Definir la función que actualizará el graph
@app.callback(
	Output('cajas-3d', 'figure'),
	[	Input('slider-grid-size', 'value'), 
  		Input('slider-frame', 'value'),
		Input('lidar-switch', 'value'),
		Input('annotations-switch', 'value'),
	],
	State('cajas-3d', 'relayoutData'),
	)
def update_grid_size(new_grid_size, frame_value, lidar_switch, annotations_switch, relayout_data):
	global grid_size, grid_x_max, grid_y_min, grid_y_max, grid_z_max, frame, camera, lidar_frame_list, first_time

	fig = go.Figure()
	fig.update_layout(relayout_data)

	# Actualizar los límites del grid
	grid_size = new_grid_size
	grid_x_min = -grid_size
	grid_x_max = grid_size
	grid_y_min = -grid_size
	grid_y_max = grid_size
	grid_z_max = grid_size

	# Actualizar los ejes del gráfico
	fig.update_layout(scene=dict(
		xaxis=dict(range=[grid_x_min, grid_x_max]),
		yaxis=dict(range=[grid_y_min, grid_y_max]),
		zaxis=dict(range=[grid_z_min, grid_z_max]),
		aspectmode= 'cube'
		),
		autosize=False,
	)

	# Crear una nueva tupla de fig.data con el nuevo grid
	new_data = fig.data[:1] + fig.data[2:]

	# Crear una nueva figura con la nueva tupla de fig.data
	new_fig = go.Figure(data=new_data, layout=fig.layout)

	# Draw current annotation
	args.annotations = annotations_switch
	if args.annotations:
		new_fig = utils.draw_annotations_frame(dataset, frame_list, frame_value, new_fig)
	
	# LiDAR
	args.lidar = lidar_switch
	if lidar_frame_list is None and args.lidar:
		## Frame list
		lidar_frame_list = dataset.lidar_frame_list
	# draw first pointCloud
	if args.lidar:
		new_fig.add_trace(utils.draw_lidar(dataset, lidar_frame_list, frame_value, args.lidar_res))

	new_fig.add_trace(
		go.Scatter3d(
			x=[0.0],
			y=[0.0],
			z=[0.0],
			mode='markers',
			marker=dict(
				size=0.01,
				color=[0,0,0],
				opacity=0.01
			)
		)
	)

	# Devolver la nueva figura
	frame = frame_value

	return new_fig

#-------------------------------------------------------------------------------------------------
# Ejecutar la aplicación de Dash
if __name__ == '__main__':
	app.run_server(debug=True)