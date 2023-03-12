import os
import numpy as np
import pandas as pd

import dash
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

import utils


#-------------------------------------------------------------------------------------------------
# Crear la app de Dash
app = dash.Dash()

# Definir la ruta donde se encuentran los archivos txt
data_dir = 'test_data'
frame_list = os.listdir(data_dir)
frame = 0

# Definir los params del grid
grid_res = 1. # metros por cuadrado
grid_size = 50. # metros por cuadrado
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
fig = utils.draw_frame(data_dir, frame_list, frame, fig, grid_x_min, grid_x_max, grid_y_min, grid_y_max)


# Dibujar el grid
grid = go.Scatter3d(
	x=np.arange(grid_x_min, grid_x_max, grid_res),
	y=np.arange(grid_y_min, grid_y_max, grid_res),
	z=np.arange(grid_z_min, grid_z_max, grid_res),
	mode='markers',
	marker=dict(size=1, color='black')
)
# Remove trace
#fig.data.remove(fig.data[0])
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

	new_fig = utils.draw_frame(data_dir, frame_list, frame_value, new_fig, grid_x_min, grid_x_max, grid_y_min, grid_y_max)
	frame = frame_value
	# Devolver la nueva figura
	return new_fig

#-------------------------------------------------------------------------------------------------
# Ejecutar la aplicación de Dash
if __name__ == '__main__':
	app.run_server(debug=True)