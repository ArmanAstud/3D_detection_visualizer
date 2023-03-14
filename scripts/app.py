# Copyright (C) 2023 Armando Astudillo

import os, sys
import numpy as np
import pandas as pd

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

import utils

import argparse

def str_to_bool(value):
	if value.lower() in {'false', 'f', '0', 'no', 'n'}:
		return False
	elif value.lower() in {'true', 't', '1', 'yes', 'y'}:
		return True

parser = argparse.ArgumentParser(description='3D_detection_visualizer.', fromfile_prefix_chars='@')

# Annotations
parser.add_argument('--annotations',		type=str_to_bool,	help='flag to read annotations',			default="True")
parser.add_argument('--annots_data_path',	type=str,			help='path were data is stored',			default='test_data')
parser.add_argument('--annots_format',		type=str,			help='path were data format is described',	default='cfg/pandas_annotations.txt')

# Grid Config
parser.add_argument('--grid_res',	type=float,	help='float value for grid_res',	default=1.0)
parser.add_argument('--grid_size',	type=float,	help='float value for grid_size',	default=50.0)


args = parser.parse_args()

#-------------------------------------------------------------------------------------------------
# Crear la app de Dash
app = dash.Dash()
frame = 0
frame_list = None

# Annotations
if args.annotations:
	## Frame list
	frame_list = os.listdir(args.annots_data_path)
	## Annots format
	try:
		with open(args.annots_format, "r") as annots_format_file:
			annots_format = annots_format_file.readlines()[0]
			annots_format.replace("\n","")
			annots_format = annots_format.split()
	except Exception as e:
		raise


# Definir los params del grid
grid_res = args.grid_res # metros por cuadrado
grid_size = args.grid_size # metros por cuadrado
grid_x_min = 0. # coordenada x min del grid
grid_x_max = grid_size*2. # coordenada x max del grid
grid_y_min = -grid_size # coordenada y min del grid
grid_y_max = grid_size # coordenada y max del grid
grid_z_min = 0. # coordenada y min del grid
grid_z_max = grid_size # coordenada y max del grid



# Crear la figura
fig = go.Figure()

camera = dict(
	up=dict(x=0, y=0, z=1),
	center=dict(x=0, y=0, z=0),
	eye=dict(x=-1.25, y=0, z=2)
)

fig.update_layout(scene_camera=camera)

# Leer el archivo txt
fig = utils.draw_annotations_frame(args.annots_data_path, annots_format, frame_list, frame, fig, grid_x_min, grid_x_max, grid_y_min, grid_y_max)


# Dibujar el grid
grid = go.Scatter3d(
	x=np.arange(grid_x_min, grid_x_max, grid_res),
	y=np.arange(grid_y_min, grid_y_max, grid_res),
	z=np.arange(grid_z_min, grid_z_max, grid_res),
	mode='markers',
	marker=dict(size=1, color='black')
)

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
	[Input('slider-grid-size', 'value'), Input('slider-frame', 'value')])
def update_grid_size(new_grid_size, frame_value):
	# Actualizar los límites del grid
	global grid_size, grid_x_max, grid_y_min, grid_y_max, grid_z_max, frame, camera
	
	fig = go.Figure()
	fig.update_layout(scene_camera=camera)

	grid_size = new_grid_size
	grid_x_max = grid_size * 2.
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

	# Crear el trazo del nuevo grid
	#new_grid = go.Scatter3d(
	#	x=np.arange(grid_x_min, grid_x_max, grid_res),
	#	y=np.arange(grid_y_min, grid_y_max, grid_res),
	#	z=np.arange(grid_z_min, grid_z_max, grid_res),
	#	mode='markers',
	#	marker=dict(size=1, color='black')
	#)

	# Crear una nueva tupla de fig.data con el nuevo grid
	#new_data = fig.data[:1] + (new_grid,) + fig.data[2:]
	new_data = fig.data[:1] + fig.data[2:]

	# Crear una nueva figura con la nueva tupla de fig.data
	new_fig = go.Figure(data=new_data, layout=fig.layout)

	new_fig = utils.draw_annotations_frame(args.annots_data_path, annots_format, frame_list, frame_value, new_fig, grid_x_min, grid_x_max, grid_y_min, grid_y_max)
	frame = frame_value
	# Devolver la nueva figura
	return new_fig

#-------------------------------------------------------------------------------------------------
# Ejecutar la aplicación de Dash
if __name__ == '__main__':
	app.run_server(debug=True)