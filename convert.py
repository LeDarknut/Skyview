import skyview
import time

def convert(catalog, levels, r_filename, separator, ra_f, dec_f, mag_f, bv_f) :
	with open(r_filename, "r") as f :
		lines = f.readlines()
	
	total = len(lines)
	done = 0
	step = round(total ** 0.5)
	
	p_time = time.time()
	
	for line in lines :
		
		line = line.split(separator)
		done += 1
		
		if done % step >= step - 1 :
			spent = (time.time() - p_time)
			progress = (done * 100) / total
			left = round((spent / progress) * (100 - progress))
			speed = round(done / max(spent, 0.00001))
			print(" progress :" + "% 8.1f" % progress + " %       left :" + "% 8d" % left + " s       speed :" + "% 8d" % speed + " /s", end="\r", flush=True)
		
		try :

			mag = line[mag_f[0]].strip()
			bv = line[bv_f[0]].strip()
			ra = line[ra_f[0]].strip()
			dec = line[dec_f[0]].strip()

			if ra == "" or dec == "" or mag == "" :
				continue
				
				
			if mag_f[1] == "mag" :
				mag = float(mag)
				
			level = -1

			for l in levels :
				if mag >= l[1] and mag < l[2] :
					level = l[0]
					break
				
			if level == -1 :
				continue

			if bv == "" :
				bv = mag
				
			if bv_f[1] == "bv" :
				bv = float(bv)
				
			elif bv_f[1] == "b" :
				bv = float(bv) - mag
				
			if ra_f[1] == "h m s" :
				ra_hms = ra.split(" ")
				h = int(ra_hms[0])
				m = int(ra_hms[1])
				s = float(ra_hms[2])
				
				ra = h + m / 60 + s / 3600
			elif ra_f[1] == "d" :
				
				ra = float(ra) / 15
				
			if dec_f[1] == "d m s" :
				dec_dms = dec.split(" ")
				sign = dec_dms[0][0]
				d = int(dec_dms[0][1:])
				m = int(dec_dms[1])
				s = float(dec_dms[2])
				
				if sign == "-" :
					dec = -1 * (d + m / 60 + s / 3600)
				else :
					dec = d + m / 60 + s / 3600
					
			elif dec_f[1] == "d" :
				
				dec = float(dec)

			location = skyview.Compute.ra_dec(ra, dec)
			brightness = skyview.Compute.mag(mag)
			color = skyview.Compute.bv(bv)

			catalog.add_star(level, skyview.Star(location, brightness, color))
		
		except :
			continue
			
if __name__ == "__main__" :

	bright = skyview.Catalog.create(2)
	convert(bright, [(0, -2, 2), (1, 2, 5), (2, 5, 36)], "Raw/Bright.tsv", ";", (0, "h m s"), (1, "d m s"), (2, "mag"), (3, "bv"))
	bright.save("Catalog/Bright.cat")

	hipparcos = skyview.Catalog.create(3)
	convert(hipparcos, [(0, -2, 2), (1, 2, 5), (2, 5, 7), (3, 7, 36)], "Raw/Hipparcos.tsv", ";", (2, "d"), (3, "d"), (0, "mag"), (1, "bv"))
	hipparcos.save("Catalog/Hipparcos.cat")

	combined_1 = skyview.Catalog.create(5)
	convert(combined_1, [(0, -2, 2), (1, 2, 5), (2, 5, 7), (3, 7, 9)], "Raw/Hipparcos.tsv", ";", (2, "d"), (3, "d"), (0, "mag"), (1, "bv"))
	convert(combined_1, [(4, 9, 10.5), (5, 10.5, 12)], "Raw/Tycho2.tsv", ";", (0, "d"), (1, "d"), (3, "mag"), (2, "b"))
	combined_1.save("Catalog/Combined 1 (Hipparcos, Tycho2).cat")
	