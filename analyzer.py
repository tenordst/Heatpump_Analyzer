# coding=utf-8
import sys
import random
import csv
import locale

from numpy import *
import matplotlib.pyplot as plt

ulkolampotila_index = 3
lammitys_meno_index = 5
lammitys_tulo_index = 6
kaivo_tulo_index = 7
kaivo_meno_index = 8
laskettu_meno_index = 9
asteminuutit_index = 10
toimintatila_index = 17
kayttovesi_index = 18

# Määrittää lämpötilan jolloin pumpun tulkitaan olevan päällä
kaivo_meno_raja = 2
lisalampo_raja = -400
mittauksia = 1500

def print_summary():
		print ('*** ' + file + ' ***')
		print ('Paivamaara: ' + pvm)
		print ('Mittauksia: ' + str(kokonaisaika))
		print ('Kaynnistyksia: ' + str(kaynnistykset))
		print ('Pienin asteminuutti: ' + str(min_asteminuutti))
		print ('Kaynnissa kokonaisajasta (lammitys): ' + str(float(kaynnissa_lammitys) / kokonaisaika * 100) + '%')
		print ('Kaynnissa kokonaisajasta (vesi): ' + str(float(kaynnissa_vesi) / kokonaisaika * 100) + '%')
		print ('Lisalampo paalla (min): ' + str(lisalampopaalla))
		print ('Keskimenolampotila: ' + str(menolamposumma / kokonaisaika))
		print ('Keskitulolampotila: ' + str(tulolamposumma / kokonaisaika))
		print ('Pienin kaivon tulolampo: ' + str(min_kaivo_tulo))
		print ('Pienin kaivon menolampo: ' + str(min_kaivo_meno))
		print ('Keskiulkolampotila: ' + str(lamposumma / kokonaisaika))
		# print (kokonaisaika)

def draw_graphs(file):
	# plot the data
	fig = plt.figure(num=None, figsize=(16, 10), dpi=120)
	ax1 = fig.add_subplot(1, 1, 1, title=file, xlabel="Aika")
	ax1.plot(t, kaivo_menolammot, 'b', t, kaivo_tulolammot, 'g',  t, tulolammot, 'y',  t, menolammot, 'c',  t, ulkolammot, 'm', t, kayttovesilammot, 'm', t, tavoitearvot, 'b')
	ax2 = ax1.twinx()
	ax2.plot(t,asteminuutit, 'r')
	# ax.plot(xdata1, ydata1, 'r', xdata2, ydata2, 'b')	
	# fig.show()
	fig.savefig(file + ".png")
	fig.clf()
	plt.close(fig)

		
def add_summary_csv():
		summary_writer.writerow([pvm,
		str(kaynnistykset),
		locale.format_string("%f",min_asteminuutti),
		locale.format_string("%f",float(kaynnissa_lammitys) / kokonaisaika * 100),
		locale.format_string("%f",float(kaynnissa_vesi) / kokonaisaika * 100),
		str(lisalampopaalla),
		locale.format_string("%f",menolamposumma / kokonaisaika),
		locale.format_string("%f",tulolamposumma / kokonaisaika),
		locale.format_string("%f",lamposumma / kokonaisaika),
		locale.format_string("%f",min_kaivo_tulo),
		locale.format_string("%f",min_kaivo_meno)])

locale.setlocale(locale.LC_ALL, '')		
		
path = './'
if len(sys.argv) > 1:
	path = path + sys.argv[1] + '/'

print ('Analyzing path ' + path)

# Get list of of all files in the current dir
from os import walk
f = []
for (dirpath, dirnames, filenames) in walk(path):
	for filename in filenames:
		f.append(path + filename)
	break
	
print (f)
		
with open('summary.csv', 'w', newline='') as csvfile:
	summary_writer = csv.writer(csvfile, dialect='excel')
	summary_writer.writerow(['Paivamaara'] + ['Kaynnistyksia'] + ['Pienin asteminuutti'] + ['Kaynnissa kokonaisajasta(lammitys)'] + ['Kaynnissa kokonaisajasta(vesi)'] + ['Lisalampo paalla'] + ['Keskimenolampotila'] + ['Keskitulolampotila'] + ['Keskiulkolampotila'] + ['Pienin kaivo (tulo)'] + ['Pienin kaivo (meno)'])	
	
	for file in f:
	  # Käydään läpi kaikki .LOG tiedostot
		
		if file.endswith('.LOG'):
			# Lämpösumma keskiarvojen laskemiseksi
			lamposumma = 0
			menolamposumma = 0
			tulolamposumma = 0
			kaivomenolamposumma = 0
			pvm = ''	

			kaynnistykset = 0
			kaynnissa_lammitys = 0
			kaynnissa_vesi = 0
			kokonaisaika = 0
			lisalampopaalla = 0
			
			min_kaivo_meno = 1000
			min_kaivo_tulo = 1000

			edellinen_asteminuutti = 1000
			edellinen_menolampo = 1000
			edellinen_kaivo_menolampo = 1000
			edellinen_toimintatila = 0
			
			index = 0
			min_asteminuutti = 1000
			pienenee = 0		
			merkintoja = 0
			
			with open(file, 'r') as csvfile:
				csvreader = csv.reader(csvfile, delimiter='	', quotechar='|')

				t = arange(0, mittauksia, 1)
				asteminuutit = zeros(mittauksia) 
				kaivo_menolammot = zeros(mittauksia)
				kaivo_tulolammot = zeros(mittauksia)
				menolammot = zeros(mittauksia)
				tulolammot = zeros(mittauksia) 		 				
				ulkolammot = zeros(mittauksia)
				kayttovesilammot = zeros(mittauksia)
				tavoitearvot = zeros(mittauksia)
				
				csvreader = csv.reader(csvfile, delimiter='	', quotechar='|')
				
				try:
					# skip first two rows
					csvreader.__next__()
					csvreader.__next__()
					
					for row in csvreader:
						# Check that row is fully written
						if len(row) >= 20:
							# Päivämääräksi ekan rivin päivämäärä
							if(pvm == ''): pvm = row[0]
							
							# Kaivon tulolämpötila 
							kaivo_tulolampo = float(row[kaivo_tulo_index ]) / 10
							if (min_kaivo_tulo > kaivo_tulolampo): min_kaivo_tulo = kaivo_tulolampo
							# print kaivo_tulolampo
							
							# Kaivon menolämpötila
							kaivo_menolampo = float(row[kaivo_meno_index ]) / 10
							if (min_kaivo_meno > kaivo_menolampo): min_kaivo_meno = kaivo_menolampo
							# print kaivo_menolampo
							
							# Lasketaan kaynnissa oloajat + käynnistysten määrä
							toimintatila = float(row[toimintatila_index])
							# print toimintatila
							if (toimintatila == 30): kaynnissa_lammitys = kaynnissa_lammitys + 1
							if (toimintatila == 20): kaynnissa_vesi = kaynnissa_vesi + 1
							if (edellinen_toimintatila == 10 and toimintatila > 10): kaynnistykset = kaynnistykset + 1
							
							# Asteminuutti ja onko lisälämpöpäällä
							asteminuutti = float(row[asteminuutit_index]) / 10
							# print asteminuutti
							if (min_asteminuutti > asteminuutti): min_asteminuutti = asteminuutti
							if (asteminuutti < lisalampo_raja): lisalampopaalla = lisalampopaalla + 1
							
							# Lasketaan lämposummat
							lamposumma = lamposumma + float(row[ulkolampotila_index]) / 10
							menolamposumma = menolamposumma + float(row[lammitys_meno_index]) / 10
							tulolamposumma = tulolamposumma + float(row[lammitys_tulo_index]) / 10
							
							# Talletetaan muutama arvo seuraava kierrosta varten (vertailu)
							edellinen_asteminuutti = asteminuutti
							edellinen_toimintatila = toimintatila
							
							asteminuutit[index] = asteminuutti
							kaivo_menolammot[index] = kaivo_menolampo
							kaivo_tulolammot[index] = kaivo_tulolampo
							menolammot[index] = float(row[lammitys_meno_index]) / 10
							tulolammot[index] = float(row[lammitys_tulo_index]) / 10
							ulkolammot[index] = float(row[ulkolampotila_index]) / 10
							kayttovesilammot[index] = float(row[kayttovesi_index]) / 10
							tavoitearvot[index] = float(row[laskettu_meno_index]) / 10
							index = index + 1
				
					# Login pituus/kokonaisaika on rivien määrä - 2
					kokonaisaika = csvreader.line_num - 2		

					# Luo yhteenvedot vain logeista jossa vähintään 10 tuntia logia (1 entry per minuutti)
					if (kokonaisaika > 600): 
						# Tulostetaan yhteenveto
						print_summary()
						
						# Talletaan yhteenveto tiedostoon
						add_summary_csv()
					
					#Piirretään kuvaaja
					draw_graphs(file)
				except csv.Error as e:
					print ("Parsing error " + e + " + with file " + file)
			

		


