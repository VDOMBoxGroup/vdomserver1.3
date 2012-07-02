"""Wysiwyg module contains common functions used in types"""

def get_centered_image_metrics (self, image_width, image_height, container_width, container_height) : 
	width_distance = container_width - image_width if container_width > image_width else 0
	height_distance = container_height - image_height if container_height > image_height else 0

	image_x = width_distance / 2
	image_y = height_distance / 2

	if container_width < image_width:
		image_width = container_width

	if container_height < image_height:
		image_height = container_height

	return image_x, image_y, image_width, image_height