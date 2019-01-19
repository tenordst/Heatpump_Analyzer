# coding=utf-8
import sys
import random
import csv
import locale

import numpy as np
import matplotlib.pyplot as plt

# Log csv tiedostojen indeksit
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
class AnalysisSummary:
	def __init__(self, csvfile):
		self.summary_writer = csv.writer(csvfile)
		self.summary_writer.writerow(['Paivamaara'] + ['Kaynnistyksia'] + ['Pienin asteminuutti'] + ['Kaynnissa kokonaisajasta(lammitys)'] + ['Kaynnissa kokonaisajasta(vesi)'] + ['Lisalampo paalla'] + ['Keskimenolampotila'] + ['Keskitulolampotila'] + ['Keskiulkolampotila'] + ['Pienin kaivo (tulo)'] + ['Pienin kaivo (meno)'])	

	def print_summary(self, log):
		print ('*** ' + file + ' ***')
		print ('Paivamaara: ' + log.pvm)
		print ('Mittauksia: %d' % log.kokonaisaika)
		print ('Kaynnistyksia: %d' % log.kaynnistykset)
		print ('Pienin asteminuutti: %d' % log.min_asteminuutti)
		print ('Kaynnissa kokonaisajasta (lammitys): %.2f' % float(log.kaynnissa_lammitys / log.kokonaisaika * 100) + '%')
		print ('Kaynnissa kokonaisajasta (vesi): %.2f' % float(log.kaynnissa_vesi / log.kokonaisaika * 100) + '%')
		print ('Lisalampo paalla (min): %d' % log.lisalampopaalla)
		print ('Keskimenolampotila: %.2fC' % (log.menolamposumma / log.kokonaisaika))
		print ('Keskitulolampotila: %.2fC' % (log.tulolamposumma / log.kokonaisaika))
		print ('Pienin kaivon tulolampo: %.2fC' % log.min_kaivo_tulo)		
		print ('Pienin kaivon menolampo: %.2fC' % log.min_kaivo_meno)
		print ('Keskiulkolampotila: %.2fC' % (log.lamposumma / log.kokonaisaika))

	def add_summary_csv(self, log):
		self.summary_writer.writerow([log.pvm,
		str(log.kaynnistykset),
		locale.format_string("%f",log.min_asteminuutti),
		locale.format_string("%f",float(log.kaynnissa_lammitys) / log.kokonaisaika * 100),
		locale.format_string("%f",float(log.kaynnissa_vesi) / log.kokonaisaika * 100),
		str(log.lisalampopaalla),
		locale.format_string("%f",log.menolamposumma / log.kokonaisaika),
		locale.format_string("%f",log.tulolamposumma / log.kokonaisaika),
		locale.format_string("%f",log.lamposumma / log.kokonaisaika),
		locale.format_string("%f",log.min_kaivo_tulo),
		locale.format_string("%f",log.min_kaivo_meno)])

class Log:
	def __init__(self):
		# Lämpösumma keskiarvojen laskemiseksi
		self.lamposumma = 0
		self.menolamposumma = 0
		self.tulolamposumma = 0
		self.pvm = ''	

		self.kaynnistykset = 0
		self.kaynnissa_lammitys = 0
		self.kaynnissa_vesi = 0
		self.kokonaisaika = 0
		self.lisalampopaalla = 0
		
		self.min_kaivo_meno = 1000
		self.min_kaivo_tulo = 1000
		self.min_asteminuutti = 1000
		
		self.t = np.arange(0, mittauksia, 1)
		self.asteminuutit = np.zeros(mittauksia) 
		self.kaivo_menolammot = np.zeros(mittauksia)
		self.kaivo_tulolammot = np.zeros(mittauksia)
		self.menolammot = np.zeros(mittauksia)
		self.tulolammot = np.zeros(mittauksia) 	
		self.ulkolammot = np.zeros(mittauksia) 	 				
		self.analyzeulkolammot = np.zeros(mittauksia)
		self.kayttovesilammot = np.zeros(mittauksia)
		self.tavoitearvot = np.zeros(mittauksia)

	def analyze(self, file):
		if file.endswith('.LOG'):			
			with open(file, 'r') as csvfile:
				csvreader = csv.reader(csvfile, delimiter='	', quotechar='|')
				index = 0
				edellinen_asteminuutti = 1000
				edellinen_toimintatila = 0
				
				try:
					# skip first two rows
					csvreader.__next__()
					csvreader.__next__()
					
					for row in csvreader:
						# Check that row is fully written
						if len(row) >= 20:
							# Päivämääräksi ekan rivin päivämäärä
							if(self.pvm == ''): self.pvm = row[0]
							
							# Kaivon tulolämpötila 
							kaivo_tulolampo = float(row[kaivo_tulo_index ]) / 10
							if (self.min_kaivo_tulo > kaivo_tulolampo): self.min_kaivo_tulo = kaivo_tulolampo
							
							# Kaivon menolämpötila
							kaivo_menolampo = float(row[kaivo_meno_index ]) / 10
							if (self.min_kaivo_meno > kaivo_menolampo): self.min_kaivo_meno = kaivo_menolampo
							
							# Lasketaan kaynnissa oloajat + käynnistysten määrä
							toimintatila = float(row[toimintatila_index])
							# print toimintatila
							if (toimintatila == 30): self.kaynnissa_lammitys = self.kaynnissa_lammitys + 1
							if (toimintatila == 20): self.kaynnissa_vesi = self.kaynnissa_vesi + 1
							if (edellinen_toimintatila == 10 and toimintatila > 10): 
								self.kaynnistykset = self.kaynnistykset + 1
							
							# Asteminuutti ja onko lisälämpöpäällä
							asteminuutti = float(row[asteminuutit_index]) / 10
							# print asteminuutti
							if (self.min_asteminuutti > asteminuutti): self.min_asteminuutti = asteminuutti
							if (asteminuutti < lisalampo_raja): self.lisalampopaalla = self.lisalampopaalla + 1
							
							# Lasketaan lämposummat
							self.lamposumma = self.lamposumma + float(row[ulkolampotila_index]) / 10
							self.menolamposumma = self.menolamposumma + float(row[lammitys_meno_index]) / 10
							self.tulolamposumma = self.tulolamposumma + float(row[lammitys_tulo_index]) / 10
							
							# Talletetaan muutama arvo seuraava kierrosta varten (vertailu)
							edellinen_asteminuutti = asteminuutti
							edellinen_toimintatila = toimintatila
							
							self.asteminuutit[index] = asteminuutti
							self.kaivo_menolammot[index] = kaivo_menolampo
							self.kaivo_tulolammot[index] = kaivo_tulolampo
							self.menolammot[index] = float(row[lammitys_meno_index]) / 10
							self.tulolammot[index] = float(row[lammitys_tulo_index]) / 10
							self.ulkolammot[index] = float(row[ulkolampotila_index]) / 10
							self.kayttovesilammot[index] = float(row[kayttovesi_index]) / 10
							self.tavoitearvot[index] = float(row[laskettu_meno_index]) / 10
							index = index + 1
				
					# Login pituus/kokonaisaika on rivien määrä - 2
					self.kokonaisaika = csvreader.line_num - 2
					return True

				except csv.Error as e:
					print ("Parsing error " + e + " + with file " + file)
		return False
			

	def draw_graphs(self, file):
		# plot the data
		fig = plt.figure(num=None, figsize=(16, 10), dpi=120)
		ax1 = fig.add_subplot(1, 1, 1, title=file, xlabel="Aika")
		ax1.plot(self.t, self.kaivo_menolammot, 'b',self.t, self.kaivo_tulolammot, 'g',  self.t, self.tulolammot, 'y',  self.t, self.menolammot, 'c', self.t, self.ulkolammot, 'm', self.t, self.kayttovesilammot, 'm', self.t, self.tavoitearvot, 'b')
		ax2 = ax1.twinx()
		ax2.plot(self.t,self.asteminuutit, 'r')
		# ax.plot(xdata1, ydata1, 'r', xdata2, ydata2, 'b')	
		# fig.show()
		fig.savefig(file + ".png")
		fig.clf()
		plt.close(fig)

# Pääfunktio
locale.setlocale(locale.LC_ALL, '')		
		
path = './'
if len(sys.argv) > 1:
	path = path + sys.argv[1] + '/'

# Get list of of all files in the current dir
from os import walk
f = []
for (dirpath, dirnames, filenames) in walk(path):
	for filename in filenames:
		f.append(path + filename)
	break
		
with open(path + 'summary.csv', 'w', newline='') as csvfile:	
	summary = AnalysisSummary(csvfile)
	for file in f:
		log = Log()
		# Analysoidaan kaikki .LOG tiedostot
		if log.analyze(file):
			# Luo yhteenvedot vain logeista jossa vähintään 10 tuntia logia (1 entry per minuutti)
			if (log.kokonaisaika > 600): 
				# Tulostetaan yhteenveto
				summary.print_summary(log)
				
				# Talletaan yhteenveto tiedostoon
				summary.add_summary_csv(log)
			
			# Piirretään kuvaaja
			log.draw_graphs(file)
		
		

		


