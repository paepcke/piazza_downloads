'''
Created on Mar 1, 2017

@author: paepcke
'''
import csv
import os

from change_point_detection import ChangePointModel


stats_file = '%s/EclipseWorkspaces/piazza_downloads/stats/cs229/fall16/top_statistics_student.csv' % os.getenv('HOME')

if __name__ == '__main__':
  reader = csv.DictReader(open(stats_file,'r'))
  ts = [float(row['Weighted Out Degree']) for row in reader]
  if len(ts)>2:
      change_pt_model = ChangePointModel()
      cusum_points = change_pt_model.compute_cusum_ts(ts)
      print(cusum_points)
      #change_pt_model.run(ts)
      #stats_file.plot(ts,'../figures/'+course+'/'+'changepoint_'+'outdeg'+course_dir+'.png','Weighted Out Degree')
    