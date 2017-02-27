#!/usr/bin/python
import matplotlib.pyplot as plt
import sys
import os
import csv
import numpy as np
from os.path import basename, splitext
from constants import *

class smallMultiples:
  def __init__(self, rows, cols):
      self.rows = rows
      self.cols = cols
      plt.figure(1)
      font = {'weight' : 'medium',
              'size'   : 5}
      plt.rc('font', **font)
      plt.subplots_adjust(hspace=0.5)

      # These are the "Tableau 20" colors as RGB.    
      tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
                   (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
                   (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
                   (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
                   (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]    
        
      # Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.    
      for i in range(len(tableau20)):    
          r, g, b = tableau20[i]    
          tableau20[i] = (r / 255., g / 255., b / 255.)

  def plot(self,parameter):
      n=1
      i=1
      for course in COURSES:
        print course  
        i+=6
        for root, dirs, files in os.walk('../stats/'+course+'/'):
            for course_dir in dirs:
              top_student_statistics = root + course_dir + '/top_statistics_student.csv'
              f_top_students = open(top_student_statistics,'r')
              reader = csv.DictReader(f_top_students)

              plt.subplot(self.rows, self.cols, n)

              if parameter == 'Pagerank':
                plt.axis([0, 15, 0, 0.1])
                y = [float(row['Pagerank']) for row in reader]
                
              elif parameter == 'Weighted Out Degree':
                plt.axis([0, 13, 0, 100])
                y = [float(row['Weighted Out Degree']) for row in reader]
                
              if not y: 
                continue

              x = range(1,len(y)+1)

              plt.xticks([])
              plt.yticks([])
              plt.title(course+' '+course_dir)
              plt.plot(x, y, linewidth=1.5,color='blue')#tableau20[(n-1)%len(tableau20)])
              n+=1
        n=i
      plt.show()

if __name__ == "__main__":
  sm  = smallMultiples(8,6)
  sm.plot('Pagerank')
