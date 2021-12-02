import math

def from_binary(f, length, signed = False, ratio = False) :
	value = int.from_bytes(f.read(length), byteorder = "big", signed = signed)
	if ratio :
		if signed :
			value /= 2 ** (8 * length - 1) - 1
		else :
			value /= 2 ** (8 * length) - 1
	return value

def to_binary(f, value, length, signed = False, ratio = False) :
	if ratio :
		if signed :
			value *= 2 ** (8 * length - 1) - 1
		else :
			value *= 2 ** (8 * length) - 1
	f.write(round(value).to_bytes(length, byteorder = "big", signed = signed))
	
class Vector :
	
	def __init__(self, x, y, z) :
		self.x = x
		self.y = y
		self.z = z
	
	def normalize(self, l = 1) :
		length = l / (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
		self.x *= length
		self.y *= length
		self.z *= length
		
	def write(self, f) :
		
		to_binary(f, self.x, 4, True, True)
		to_binary(f, self.y, 4, True, True)
		to_binary(f, self.z, 4, True, True)
		
	@staticmethod
	def read(f) :
		
		x = from_binary(f, 4, True, True)
		y = from_binary(f, 4, True, True)
		z = from_binary(f, 4, True, True)
		
		return Vector(x, y, z)
		
		
class Angle :
	
	def __init__(self, angle) :
		self.angle = angle
		
	def write(self, f) :
		
		to_binary(f, self.angle / math.pi, 3, False, True)
		
	@staticmethod
	def read(f) :
		
		angle = from_binary(f, 3, False, True) * math.pi
		
		return Angle(angle)
		
class Color :
	
	def __init__(self, r, g, b) :
		self.r = r
		self.g = g
		self.b = b

	def write(self, f) :
		
		to_binary(f, self.r, 1, False, False)
		to_binary(f, self.g, 1, False, False)
		to_binary(f, self.b, 1, False, False)
		
	@staticmethod
	def read(f) :
		
		r = from_binary(f, 1, False, False)
		g = from_binary(f, 1, False, False)
		b = from_binary(f, 1, False, False)
		
		return Color(r, g, b)

class Brightness :
	
	def __init__(self, brightness) :
		self.brightness = brightness
		
	def write(self, f) :
		
		to_binary(f, self.brightness, 1, False, True)
	
	@staticmethod
	def read(f) :
		
		brightness = from_binary(f, 1, False, True)
		
		return Brightness(brightness)
		
class Star :
	
	def __init__(self, location, brightness, color) :
		self.location = location
		self.brightness = brightness
		self.color = color
			
	def write(self, f) :
		
		self.location.write(f)
		self.brightness.write(f)
		self.color.write(f)
		
	@staticmethod
	def read(f) :
		
		location = Vector.read(f)
		brightness = Brightness.read(f)
		color = Color.read(f)
		
		return Star(location, brightness, color)

class Div :
	
	def __init__(self, center, radius, stars, divs) :
		self.center = center
		self.radius = radius
		self.stars = stars
		self.divs = divs
		
	def write(self, f) :
		
		self.center.write(f)
		self.radius.write(f)
		
		def content(div) :
			size = 5 + len(div.stars) * 16
			for sub_div in div.divs :
				size += content(sub_div) + 19
			return size
		
		to_binary(f, content(self), 4, False, False)
		
		to_binary(f, len(self.stars), 4, False, False)
		for star in self.stars :
			star.write(f)
		to_binary(f, len(self.divs), 1, False, False)
		for div in self.divs :
			div.write(f)
		
	@staticmethod
	def read(f) :

		center = Vector.read(f)
		radius = Angle.read(f)
		
		f.read(4)
		
		stars = []
		for i_star in range(from_binary(f, 4, False, False)) :
			stars.append(Star.read(f))
		divs = []
		for i_div in range(from_binary(f, 1, False, False)) :
			divs.append(Div.read(f))

		return Div(center, radius, stars, divs)

		
class Catalog :
	
	def __init__(self, level, div) :
		self.level = level
		self.div = div
		
	@staticmethod
	def create(level) :
		
		divs = []
		
		if level > 0 :
		
			c = []
				
			rings = (
				(0, 1, 0),
				(math.pi / 2 - math.atan(1 / 2), 5, 0),
				(math.pi / 2 + math.atan(1 / 2), 5, math.pi / 5),
				(math.pi, 1, 0)
			) #(theta, number of vertex, phi offset)
			
			for ring in rings  :
				
				t = ring[0]
				
				c.append([])
							
				for i in range(ring[1]) :
					
					p = (i / ring[1]) * 2 * math.pi + ring[2]
					
					x = math.sin(t) * math.cos(p)
					y = math.sin(t) * math.sin(p)
					z = math.cos(t)
					
					c[-1].append(Vector(x, y, z))
					
			faces = (
			
				(c[0][0], c[1][0], c[1][1]),
				(c[0][0], c[1][1], c[1][2]),
				(c[0][0], c[1][2], c[1][3]),
				(c[0][0], c[1][3], c[1][4]),
				(c[0][0], c[1][4], c[1][0]),
				
				(c[1][0], c[1][1], c[2][0]),
				(c[1][1], c[1][2], c[2][1]),
				(c[1][2], c[1][3], c[2][2]),
				(c[1][3], c[1][4], c[2][3]),
				(c[1][4], c[1][0], c[2][4]),
				
				(c[2][0], c[2][1], c[1][1]),
				(c[2][1], c[2][2], c[1][2]),
				(c[2][2], c[2][3], c[1][3]),
				(c[2][3], c[2][4], c[1][4]),
				(c[2][4], c[2][0], c[1][0]),
				
				(c[3][0], c[2][0], c[2][1]),
				(c[3][0], c[2][1], c[2][2]),
				(c[3][0], c[2][2], c[2][3]),
				(c[3][0], c[2][3], c[2][4]),
				(c[3][0], c[2][4], c[2][0])
			
			)
			
			def sface(l, level, a, b, c, ab, bc, ca) :
				a.normalize()
				b.normalize()
				c.normalize()
				
				ab.normalize()
				bc.normalize()
				ca.normalize()
				
				if l < level :
						
					aab = Vector((a.x + ab.x) / 2, (a.y + ab.y) / 2, (a.z + ab.z) / 2)
					abb = Vector((b.x + ab.x) / 2, (b.y + ab.y) / 2, (b.z + ab.z) / 2)
					
					bbc = Vector((b.x + bc.x) / 2, (b.y + bc.y) / 2, (b.z + bc.z) / 2)
					bcc = Vector((c.x + bc.x) / 2, (c.y + bc.y) / 2, (c.z + bc.z) / 2)
					
					cca = Vector((c.x + ca.x) / 2, (c.y + ca.y) / 2, (c.z + ca.z) / 2)
					caa = Vector((a.x + ca.x) / 2, (a.y + ca.y) / 2, (a.z + ca.z) / 2)
					
					abc = Vector((a.x + ab.x + bc.x + ca.x) / 4, (a.y + ab.y + bc.y + ca.y) / 4, (a.z + ab.z + bc.z + ca.z) / 4)
					bca = Vector((b.x + ab.x + bc.x + ca.x) / 4, (b.y + ab.y + bc.y + ca.y) / 4, (b.z + ab.z + bc.z + ca.z) / 4)
					cab = Vector((c.x + ab.x + bc.x + ca.x) / 4, (c.y + ab.y + bc.y + ca.y) / 4, (c.z + ab.z + bc.z + ca.z) / 4)
					
					divs = [
						sface(l + 1, level,  a, ab, ca, aab, abc, caa),
						sface(l + 1, level, ab,  b, bc, abb, bbc, bca),
						sface(l + 1, level, ca, bc,  c, cab, bcc, cca),
						sface(l + 1, level, bc, ca, ab, cab, abc, bca)
					]
				
				else :
					
					divs = []
					
				center = Vector((a.x + b.x + c.x) / 3, (a.y + b.y + c.y) / 3, (a.z + b.z + c.z) / 3)
				center.normalize()
				
				radius = Angle(max(
					math.acos(a.x * center.x + a.y * center.y + a.z * center.z),
					math.acos(b.x * center.x + b.y * center.y + b.z * center.z),
					math.acos(c.x * center.x + c.y * center.y + c.z * center.z)
				))
			
				return Div(center, radius, [], divs)
			
			for face in faces :
				a = face[0]
				b = face[1]
				c = face[2]
				
				ab = Vector((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2)
				bc = Vector((b.x + c.x) / 2, (b.y + c.y) / 2, (b.z + c.z) / 2)
				ca = Vector((c.x + a.x) / 2, (c.y + a.y) / 2, (c.z + a.z) / 2)
			
				divs.append(sface(1, level, a, b, c, ab, bc, ca))
		
		return Catalog(level, Div(Vector(0, 0, 1), Angle(math.pi), [], divs))
			
	def add_star(self, level, star) :
		
		if level == 0 :
			self.div.stars.append(star)
		else :
		
			divs = self.div.divs
			
			for l in range(level) :
				
				best_distance = 4
				
				for div in divs :
			
					distance = (div.center.x - star.location.x) ** 2 + (div.center.y - star.location.y) ** 2 + (div.center.z - star.location.z) ** 2
					if distance < best_distance :
						best_distance = distance
						best = div
						
				if l + 1 != level :
					divs = best.divs
				else:
					best.stars.append(star)
			
		
	def write(self, f) :
		
		to_binary(f, self.level, 1, False, False)
		self.div.write(f)
		
	@staticmethod
	def read(f) :
		
		level = from_binary(f, 1, False, False)
		div = Div.read(f)
		
		return Catalog(level, div)
		
	def save(self, filename) :
		with open(filename, "wb") as f :
			self.write(f)
			
class Camera :

	def __init__(self, location, anchor) :
			
		self.location = location
		self.anchor = anchor
			
	def move(self, fixed, angle, speed) :
		
		if fixed :

			v_a = Vector(self.anchor.x - self.location.x, self.anchor.y - self.location.y, self.anchor.z - self.location.z)
			f_a = v_a.x * self.location.x + v_a.y * self.location.y + v_a.z * self.location.z
			
			cos_a = math.cos(angle)
			sin_a = math.sin(angle)
			
			self.anchor.x = self.location.x + (v_a.x * cos_a + (v_a.y * self.location.z - v_a.z * self.location.y) * sin_a + self.location.x * f_a * (1 - cos_a)) * speed
			self.anchor.y = self.location.y + (v_a.y * cos_a + (v_a.z * self.location.x - v_a.x * self.location.z) * sin_a + self.location.y * f_a * (1 - cos_a)) * speed
			self.anchor.z = self.location.z + (v_a.z * cos_a + (v_a.x * self.location.y - v_a.y * self.location.x) * sin_a + self.location.z * f_a * (1 - cos_a)) * speed
			
			self.anchor.normalize()
				
		else :
			
			v_a = Vector(self.anchor.x - self.location.x, self.anchor.y - self.location.y, self.anchor.z - self.location.z)
			f_a = v_a.x * self.location.x + v_a.y * self.location.y + v_a.z * self.location.z
			
			cos_a = math.cos(angle)
			sin_a = math.sin(angle)
			
			self.anchor.x = self.location.x + v_a.x * cos_a + (v_a.y * self.location.z - v_a.z * self.location.y) * sin_a + self.location.x * f_a * (1 - cos_a)
			self.anchor.y = self.location.y + v_a.y * cos_a + (v_a.z * self.location.x - v_a.x * self.location.z) * sin_a + self.location.y * f_a * (1 - cos_a)
			self.anchor.z = self.location.z + v_a.z * cos_a + (v_a.x * self.location.y - v_a.y * self.location.x) * sin_a + self.location.z * f_a * (1 - cos_a)
				
			v_b = Vector(self.location.x - self.anchor.x, self.location.y - self.anchor.y, self.location.z - self.anchor.z)
			f_b = v_b.x * self.anchor.x + v_b.y * self.anchor.y + v_b.z * self.anchor.z
			
			self.location.x -= v_b.x * speed
			self.location.y -= v_b.y * speed
			self.location.z -= v_b.z * speed
			
			self.anchor.x += (-v_b.x + self.anchor.x * f_b * 2) * speed
			self.anchor.y += (-v_b.y + self.anchor.y * f_b * 2) * speed
			self.anchor.z += (-v_b.z + self.anchor.z * f_b * 2) * speed
			
			self.location.normalize()
			self.anchor.normalize()
			
			v_c = Vector(self.anchor.x - self.location.x, self.anchor.y - self.location.y, self.anchor.z - self.location.z)
			f_c = v_c.x * self.location.x + v_c.y * self.location.y + v_c.z * self.location.z
			
			cos_c = math.cos(-angle)
			sin_c = math.sin(-angle)
				
			self.anchor.x = self.location.x + v_c.x * cos_c + (v_c.y * self.location.z - v_c.z * self.location.y) * sin_c + self.location.x * f_c * (1 - cos_c)
			self.anchor.y = self.location.y + v_c.y * cos_c + (v_c.z * self.location.x - v_c.x * self.location.z) * sin_c + self.location.y * f_c * (1 - cos_c)
			self.anchor.z = self.location.z + v_c.z * cos_c + (v_c.x * self.location.y - v_c.y * self.location.x) * sin_c + self.location.z * f_c * (1 - cos_c)
			
		
class View :
	
	def __init__(self, location, anchor, frame, rotation, stars) :
		self.location = location
		self.anchor = anchor
		self.frame = frame
		self.rotation = rotation
		self.stars = stars
		
	@staticmethod	
	def catalog_file(filename, camera, max_level = 10, sensitivity = 50, min_weight = 0.1) :
		
		origin = Origin(camera.location)
		
		v_anchor = origin.apply(camera.anchor)
		
		frame = Angle(math.acos(camera.location.x * camera.anchor.x + camera.location.y * camera.anchor.y + camera.location.z * camera.anchor.z))
		
		if v_anchor.x > 0 :
			rotation = Angle(-math.atan(v_anchor.y / v_anchor.x))
		elif v_anchor.x < 0 :
			rotation = Angle(-math.atan(v_anchor.y / v_anchor.x) + math.pi)
		else :
			if v_anchor.y <= 0 :
				rotation = Angle(math.pi / 2)
			else :
				rotation = Angle(3 * math.pi / 2)
			
		stars = []
		
		target_weight = (((frame.angle / math.pi) ** 0.2 * 0.75) - 0.5)
		filter_power = 100 / sensitivity
		
		with open(filename, "rb") as f :
			
			level = from_binary(f, 1, False, False)
			
			def explore_div(l, stars, f) :
				center = Vector.read(f)
				radius = Angle.read(f)
				
				distance = math.acos(camera.location.x * center.x + camera.location.y * center.y + camera.location.z * center.z)
				
				if l <= max_level and distance <= frame.angle + radius.angle:
					
					f.read(4)
				
					for i_star in range(from_binary(f, 4, False, False)) :
						
						star = Star.read(f)

						v_location = origin.apply(star.location)
						
						t = Angle(math.acos(v_location.z / ((v_location.x ** 2 + v_location.y ** 2 + v_location.z ** 2) ** 0.5)))
						if v_location.x > 0 :
							p = Angle(math.atan(v_location.y / v_location.x))
						elif v_location.x < 0 :
							p = Angle(math.atan(v_location.y / v_location.x) + math.pi)
						else :
							if v_location.y <= 0 :
								p = Angle(math.pi / 2)
							else :
								p = Angle(3 * math.pi / 2)
							
							
						if t.angle < frame.angle :
							b = star.brightness.brightness - target_weight
							if b < 0.5 :
								if b < 0 :
									weight = 0
								else :
									weight = 0.5 * (b * 2) ** filter_power
							else :
								if b > 1 :
									weight = 1
								else :
									weight = 1 - (0.5 * (2 - b * 2) ** filter_power)
									
							if weight > min_weight :
								stars.append((p.angle + rotation.angle, t.angle / frame.angle, weight, (star.color.r, star.color.g, star.color.b)))
					
					for i_div in range(from_binary(f, 1, False, False)) :
						explore_div(l + 1, stars, f)
					
				else :
					
					f.read(from_binary(f, 4, False, False))
			
			stars = []
			explore_div(0, stars, f)

		return View(camera.location, camera.anchor, frame, rotation, sorted(stars, key = lambda star : star[2], reverse = True))
			
	def svg(self, b_filename, s_filename, w, h, r_min, r_max) :
		
		diagonal = (w ** 2 + h ** 2) ** 0.5
		
		with open(s_filename, "w") as svg :

			with open(b_filename, "r") as b :
				base = b.read()
				
				stars = []
				
				for star in self.stars :
					x = 0.5 * (w + math.cos(star[0]) * star[1] * diagonal)
					y = 0.5 * (h + math.sin(star[0]) * star[1] * diagonal)
					r = r_min + (r_max - r_min) * star[2]
					stars.append("<circle cx=\"" + str(x) + "\" cy=\"" + str(y) + "\" r=\"" + str(r) + "\" fill=\"rgb" + str(star[3]) + "\" fill-opacity=\"" + str(star[2]) + "\"/>")
					
			svg.write(base.replace("%W%", str(w)).replace("%H%", str(h)).replace("%STAR%", "\n\t\t".join(stars)))

class Origin :
	
	def __init__(self, location) :
		
		t = math.acos(location.z)
		if location.x > 0 :
			p = math.atan(location.y / location.x)
		elif location.x < 0 :
			p = math.atan(location.y / location.x) + math.pi
		else :
			if location.y <= 0 :
				p = math.pi / 2
			else :
				p = 3 * math.pi / 2
		
		cos_t = math.cos(t)
		cos_p = math.cos(p)
		sin_t = math.sin(t)
		sin_p = math.sin(p)
		
		self.x1 = cos_t * cos_p
		self.x2 = cos_t * sin_p
		self.x3 = -sin_t
		self.y1 = -sin_p
		self.y2 = cos_p
		self.z1 = sin_t * cos_p
		self.z2 = sin_t * sin_p
		self.z3 = cos_t
		
	def apply(self, vector) :
		x = vector.x * self.x1 + vector.y * self.x2 + vector.z * self.x3
		y = vector.x * self.y1 + vector.y * self.y2
		z = vector.x * self.z1 + vector.y * self.z2 + vector.z * self.z3
		
		return Vector(x, y, z)
		
class Compute :
		
	bv_table = (
		(188, 252, 255),
		(192, 252, 255),
		(196, 252, 255),
		(200, 253, 255),
		(204, 253, 255),
		(208, 253, 255),
		(212, 253, 255),
		(217, 253, 255),
		(221, 253, 255),
		(226, 253, 255),
		(230, 253, 255),
		(235, 253, 255),
		(239, 253, 255),
		(244, 252, 255),
		(248, 252, 255),
		(253, 252, 255),
		(255, 251, 255),
		(255, 251, 255),
		(255, 250, 255),
		(255, 250, 250),
		(255, 249, 241),
		(255, 248, 233),
		(255, 248, 224),
		(255, 247, 216),
		(255, 246, 209),
		(255, 245, 201),
		(255, 245, 194),
		(255, 244, 187),
		(255, 243, 180),
		(255, 242, 173),
		(255, 241, 167),
		(255, 240, 161),
		(255, 239, 155),
		(255, 238, 149),
		(255, 237, 143),
		(255, 236, 138),
		(255, 224,  94),
		(255, 223,  88),
		(255, 221,  83),
		(255, 219,  78),
		(255, 217,  73),
		(255, 215,  68),
		(255, 213,  64),
		(255, 210,  59),
		(255, 208,  55),
		(255, 206,  51),
		(255, 204,  46),
		(255, 201,  43),
		(255, 199,  39)
	)

	def bv(bv, raw = False) :
		
		bv = min(max(bv, -0.4), 2)
		
		if raw :
			
			t = 4600 * ((1 / ((0.92 * bv) + 1.7)) + (1 / ((0.92 * bv) + 0.62)))


			if t >= 1667 and t <= 4000 :
				x = (-0.2661239 * ((10 ** 9) / (t ** 3))) - (-0.2343580 * ((10 ** 6) / (t ** 2))) + (0.8776956 * ((10 ** 3) / t)) + 0.179910
			elif t >= 4000 and t <= 25000 :
				x = (-3.0258469 * ((10 ** 9) / (t ** 3))) + (2.1070379 * ((10 ** 6) / (t ** 2))) + (0.2226347 * ((10 ** 3) / t)) + 0.240390

			if t >= 1667 and t <= 2222 :
				y = (-1.1063814 * (x ** 3)) -(1.34811020 * (x ** 2)) + (2.18555832 * x) - 0.20219683
			elif t >= 2222 and t <= 4000 :
				y = (-0.9549476 * (x ** 3)) - (1.37418593 * (x ** 2)) + (2.09137015 * x) - 0.16748867
			elif t >= 4000 and t <= 25000 :
				y = (3.0817580 * (x ** 3)) - (5.87338670 * (x ** 2)) + (3.75112997 * x) - 0.37001483
			
			
			if y == 0 :
				Y = 0
				X = 0
				Z = 0
			else :
				Y = 1
				X = (x * Y) / y
				Z = ((1 - x - y) * Y) / y


			r = (3.2406 * X) + (-1.5372 * Y) + (-0.4986 * Z)
			g = (-0.9689 * X) + (1.8758 * Y) + (0.0415 * Z)
			b = (0.0557 * X) + (-0.2040 * Y) + (1.0570 * Z)
			
			r = min(max(int(r * 255), 0), 255)
			g = min(max(int(g * 255), 0), 255)
			b = min(max(int(b * 255), 0), 255)
			
		else :
			
			r, g, b = Compute.bv_table[round((bv + 0.4) * 20)]
			
			
		return Color(r, g, b)

	def mag(mag) :
		
		return Brightness(min(max(1 / (1.2 ** ((1.44 + mag) * math.log(2.5))), 0), 1))

	def ra_dec(ra, dec, angle = False) :
		
		if angle == False :
			
			t = ((90 - dec) / 180) * math.pi
			p = (ra / 12) * math.pi
			
			location = Vector(math.sin(t) * math.cos(p), math.sin(t) * math.sin(p), math.cos(t))
			
			return location
			
		else : 
			
			t = ((90 - dec) / 180) * math.pi
			p = (ra / 12) * math.pi
			a = (angle / 360) * math.pi
			
			location = Vector(math.sin(t) * math.cos(p), math.sin(t) * math.sin(p), math.cos(t))
			
			if t + a < math.pi :
				
				anchor = Vector(math.sin(t + a) * math.cos(p), math.sin(t + a) * math.sin(p), math.cos(t + a))
				
				cos_a = math.cos(math.pi * 0.5)
				sin_a = math.sin(math.pi * 0.5)
				
			else :
				
				anchor = Vector(math.sin(t - a) * math.cos(p), math.sin(t - a) * math.sin(p), math.cos(t - a))
				
				cos_a = math.cos(math.pi * 1.5)
				sin_a = math.sin(math.pi * 1.5)

				
			v_a = Vector(anchor.x - location.x, anchor.y - location.y, anchor.z - location.z)
			f_a = v_a.x * location.x + v_a.y * location.y + v_a.z * location.z
			
			anchor.x = location.x + v_a.x * cos_a + (v_a.y * location.z - v_a.z * location.y) * sin_a + location.x * f_a * (1 - cos_a)
			anchor.y = location.y + v_a.y * cos_a + (v_a.z * location.x - v_a.x * location.z) * sin_a + location.y * f_a * (1 - cos_a)
			anchor.z = location.z + v_a.z * cos_a + (v_a.x * location.y - v_a.y * location.x) * sin_a + location.z * f_a * (1 - cos_a)
			
			anchor.normalize()
			
			return location, anchor
		
	def deg(deg) :
	
		angle = (deg / 180) * math.pi
		
		return Angle(angle)