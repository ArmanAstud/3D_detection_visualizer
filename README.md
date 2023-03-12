# 3D_detection_visualizer
This is a visualization tool for 3D detection pipelines.

## Install it
`python3 -m pip install -r requirements.txt`

## Annotation's format
### 1. 3D Labels
&emsp;`x y z yaw h w l score label`

&emsp;Where:  
&emsp;&emsp;1. `x`:&emsp;&emsp;&emsp;&emsp;Obstacle's Center X position (Axis X->forward)  
&emsp;&emsp;2. `y`:&emsp;&emsp;&emsp;&emsp;Obstacle's Center Y position (Axis Y->left)  
&emsp;&emsp;3. `z`:&emsp;&emsp;&emsp;&emsp;Obstacle's Grounded Z position (Axis Z->up)  
&emsp;&emsp;4. `yaw`:&emsp;&emsp;&emsp;Obstacle's yaw angle (heading to ego-right)  
&emsp;&emsp;5. `h`:&emsp;&emsp;&emsp;&emsp;Obstacle's Height dimension  
&emsp;&emsp;6. `w`:&emsp;&emsp;&emsp;&emsp;Obstacle's Widht dimension  
&emsp;&emsp;7. `l`:&emsp;&emsp;&emsp;&emsp;Obstacle's Length dimension  
&emsp;&emsp;8. `score`:&emsp;&emsp;Obstacle's detection Score (0.0->1.0)  
&emsp;&emsp;9. `label`:&emsp;&emsp;Obstacle's detection Label  

## Launch it
`python3 scripts/app.py`

## Visualize
Open the link http://127.0.0.1:8050/