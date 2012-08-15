"""Wysiwyg module contains common functions used in types"""

def get_centered_image_metrics (image_width, image_height, container_width, container_height) : 
	width_distance = container_width - image_width if container_width > image_width else 0
	height_distance = container_height - image_height if container_height > image_height else 0

	image_x = width_distance / 2
	image_y = height_distance / 2

	if container_width < image_width:
		image_width = container_width

	if container_height < image_height:
		image_height = container_height

	return image_x, image_y, image_width, image_height
	
def get_empty_wysiwyg_value (type, image_id) :
	image_width = image_height = 50
	image_x = image_y = 0
	
	if not type.width:
		type.width = "0"
	
	if not type.height:
		type.height = "0"
		
	image_x, image_y, image_width, image_height = get_centered_image_metrics( image_width, image_height, int(type.width), int(type.height) )
											
	result=\
			u"""<container id="{id}" zindex="{zindex}" hierarchy="{hierarchy}" top="{top}" left="{left}" 
							width="{width}" height="{height}" backgroundcolor="#f0f0f0" bordercolor="#000000">
					<svg>
						<image x="{image_x}" y="{image_y}" href="#Res({image_id})" width="{image_width}" height="{image_height}"/>
					</svg>
				</container>""".format(id = type.id,
										zindex = type.zindex, 
										hierarchy = type.hierarchy, 
										top = type.top, 
										left = type.left, 
										width = type.width, 
										height = type.height,
										image_x = image_x,
										image_y = image_y,
										image_id = image_id,
										image_width = image_width,
										image_height = image_height)
	
	return result