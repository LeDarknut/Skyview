import skyview
import pygame
import math
import datetime

pygame.init()

class Render :
	
	def __init__(self, v_filename, s_filename, width, height, ra, dec, angle) :
		
		self.v_filename = v_filename
		self.s_filename = s_filename
		self.window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
		self.clock = pygame.time.Clock()
		
		location, anchor = skyview.Compute.ra_dec(ra , dec, angle)
		
		self.camera = skyview.Camera(location, anchor)
		
		self.loop()		

	def render(self, r_min = 1, r_max = 8) :
		
		self.window.fill(0)
		
		width = self.window.get_width()
		height = self.window.get_height()
		diagonal = (width ** 2 + height ** 2) ** 0.5
		
		view = skyview.View.catalog_file(self.v_filename, self.camera, 3, 60, 0.15)

		for star in view.stars :
			
			x = int(0.5 * (width + math.cos(star[0]) * star[1] * diagonal))
			y = int(0.5 * (height + math.sin(star[0]) * star[1] * diagonal))
			r = int(r_min + (r_max - r_min) * star[2])
			
			circle = pygame.Surface((r * 2, r * 2))
			circle.set_colorkey((0, 0, 0))
			circle.set_alpha(round(star[2] * 255))
			pygame.draw.circle(circle, star[3], (r, r), r)
			self.window.blit(circle, (x - r, y - r), None)
				
	def svg(self, r_min = 0.5, r_max = 4) :
		
		basename = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
		view = skyview.View.catalog_file(self.s_filename, self.camera, 3, 60, 0)

		for i in range(max(len(view.stars) // 99900, 1)) :
			s = 65536 * i
			s_view = skyview.View(view.location, view.anchor, view.frame, view.rotation, view.stars[99900 * i : min(99900 * (i + 1), len(view.stars))])
			s_view.svg("Resource/Base.svg", "Shot/" + basename + " " + str(i + 1) + ".svg", 1080, 1080, r_min, r_max)
		
		print("done")
				
	def loop(self) :
		
		speeds = [1 / 100, 1/20, 1/5]
		speed_mode = 1

		self.render()
		
		actions = []
		
		action_move_l = ["K276"]
		action_move_r = ["K275"]
		action_move_u = ["K273"]
		action_move_d = ["K274"]
		action_rotate_w = ["K99"]
		action_rotate_c = ["K118"]
		action_speed_0 = ["K49"]
		action_speed_1 = ["K50"]
		action_speed_2 = ["K51"]
		action_zoom_i = ["M4"]
		action_zoom_o = ["M5"]
		action_coordinates = ["K13"]
		action_shot = ["K32"]
		action_exit = ["K27"]


		running = True
		while running :
			for event in pygame.event.get() :
				if (event.type == pygame.KEYDOWN) :
					
					k = "K" + str(event.key)
					
					if not(k in actions) :
					
						actions.append(k)
						
				elif (event.type == pygame.KEYUP) :
					
					k = "K" + str(event.key)
					
					if k in actions :
					
						actions.remove(k)

						
				elif event.type == pygame.MOUSEBUTTONUP :
					
					m = "M" + str(event.button)
					
					if not(m in actions) :
					
						actions.append(m)
					
				elif event.type == pygame.MOUSEBUTTONDOWN :
					
					m = "M" + str(event.button)
					
					if m in actions :
					
						actions.remove(m)
						
				elif event.type == pygame.QUIT:
            
					pygame.quit()
					exit()
						
				elif event.type == pygame.VIDEORESIZE:
					
					self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
					self.render()
						
			if actions :
							
				speed = speeds[speed_mode]
				
				for action in actions :
		
					if action in action_move_l :
						
						self.camera.move(False, math.pi, speed)
						
					elif action in action_move_r :
						
						self.camera.move(False, 0, speed)
						
					elif action in action_move_u :
						
						self.camera.move(False, math.pi * 0.5, speed)
						
					elif action in action_move_d :
						
						self.camera.move(False, math.pi * 1.5, speed)
						
					elif action in action_rotate_w : 
						
						self.camera.move(True, math.pi * (speed * 0.5), 1)
						
					elif action in action_rotate_c :
						
						self.camera.move(True, math.pi * (2 - (speed * 0.5)), 1)
						
					elif action in action_speed_0 :
						
						actions.remove(action)
									
						speed_mode = 0
						
					elif action in action_speed_1 :
						
						actions.remove(action)
									
						speed_mode = 1
						
					elif action in action_speed_2 :
						
						actions.remove(action)
									
						speed_mode = 2
						
					elif action in action_zoom_i :
						
						actions.remove(action)
									
						self.camera.move(True, 0, 1 - (speed * 2))		
						
					elif action in action_zoom_o :
						
						actions.remove(action)
						
						if math.acos(self.location.x * self.anchor.x + self.location.y * self.anchor.y + self.location.z * self.anchor.z) < math.pi * 0.5 :

							self.camera.move(True, 0, 1 + (speed * 2))
							
					elif action in action_coordinates :
						
						actions.remove(action)
							
						try :
							
							ra    = float(input("ra     : "))
							dec   = float(input("dec    : "))
							angle = float(input("angle  : "))

							self.location, self.anchor = skyview.Compute.ra_dec(ra , dec, angle) 
							
						except :
							pass
						
					elif action in action_shot :
						
						actions.remove(action)
						
						self.svg()
					
					elif action in action_exit :
						
						running = False
						
					else :
						
						actions.remove(action)
				
				self.render()		
				self.clock.tick(10)

			pygame.display.flip()
		pygame.quit()
		
if __name__ == "__main__" :
		
	Render("Catalog/Bright.cat", "Catalog/Combined 1 (Hipparcos, Tycho2).cat", 1000, 600, 0, 0, 90)