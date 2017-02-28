#!/usr/bin/python
import matplotlib.pyplot as plt
import sys
import os
import csv
import operator
import numpy as np
import matplotlib.patches as mpatches

from os.path import basename, splitext
from constants import *
from pylab import *

class smallMultiples:
  def __init__(self, rows, cols):
      self.rows = rows
      self.cols = cols
      plt.figure(1)
      font = {'weight' : 'medium',
              'size'   : 5}
      plt.rc('font', **font)
      plt.subplots_adjust(hspace=0.5)
      #plt.colorbar()
      cdict = {'red': ((0.0, 0.0, 0.0),
                      (0.5, 1.0, 0.7),
                      (1.0, 1.0, 1.0)),
              'green': ((0.0, 0.0, 0.0),
                        (0.5, 1.0, 0.0),
                        (1.0, 1.0, 1.0)),
              'blue': ((0.0, 0.0, 0.0),
                       (0.5, 1.0, 0.0),
                       (1.0, 0.5, 1.0))}
      my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap',cdict,256)
      pcolor(rand(10,10),cmap=my_cmap)

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

  def get_files(self,course, parameter):
      all_x = []
      all_y = []
      names = []
      flattened_y = []

      for root, dirs, files in os.walk('../stats/'+course+'/'):
        for course_dir in sorted(dirs,key=lambda d:d[-2:]):
            #print course_dir
            top_student_statistics = root + course_dir + '/top_statistics_student.csv'
            f_top_students = open(top_student_statistics,'r')
            reader = csv.DictReader(f_top_students)
            names.append(course_dir)

            if parameter == 'Pagerank':
                y = [float(row['Pagerank']) for row in reader]
                
            elif parameter == 'Weighted Out Degree':
                y = [float(row['Weighted Out Degree']) for row in reader]

            if not y: 
                continue

            x = range(1,len(y)+1)
            all_x.append(x)
            all_y.append(y)
            flattened_y.append(len(y))

      normalized_y = [(i-min(flattened_y))/float((max(flattened_y)-min(flattened_y)+1)) for i in flattened_y]

      color_map = {flattened_y[i]:normalized_y[i] for i in range(len(flattened_y))}
      sorted_map = sorted(color_map.items(), key=operator.itemgetter(1))
      sorted_map = [(elem[0],(1,elem[1],0))  for elem in sorted_map]
      #print sorted_map
      return all_x,all_y,names,normalized_y,flattened_y


  def plot(self,parameter):
      n=1
      k=1
      for course in COURSES:
          print course  
          k+=7
          all_x,all_y,names,normalized_y,flattened_y = self.get_files(course, parameter)
          rgb = [(1,normalized_y[i],0) for i in range(len(normalized_y))]
          # patches = []
          # for i in range(len(rgb)):
          #   patches.append(mpatches.Patch(color=rgb[i], label=course+'->'+str(flattened_y[i])))
          # plt.legend(handles=patches)
          # print flattened_y, ' : ',rgb

          for i in range(len(all_x)):
              x = all_x[i]
              y = all_y[i]


              plt.subplot(self.rows, self.cols, n)

              if parameter == 'Pagerank':
                plt.axis([0, 15, 0, 0.1])
                
              elif parameter == 'Weighted Out Degree':
                plt.axis([0, 13, 0, 82])

              if not y: 
                continue

              x = range(1,len(y)+1)

              plt.xticks([])
              plt.yticks([])
              plt.title(course+' '+names[i])
              ax = plt.gca()
              ax.set_axis_bgcolor((1,normalized_y[i], 0))
              plt.plot(x, y, linewidth=1.5,color='blue')#tableau20[(n-1)%len(tableau20)])
              n+=1
          n=k
      plt.show()

if __name__ == "__main__":
  sm  = smallMultiples(8,7)
  sm.plot('Pagerank')
