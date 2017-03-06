'''
Created on Mar 1, 2017

@author: paepcke
'''
import csv
import os
import numpy as np

from change_point_detection import ChangePointModel


#stats_file = '%s/EclipseWorkspaces/piazza_downloads/stats/cs229/fall16/top_statistics_student.csv' % os.getenv('HOME')
stats_file = '%s/EclipseWorkspaces/piazza_downloads/stats/cs229/fall15/top_statistics_student.csv' % os.getenv('HOME')
#stats_file = '%s/EclipseWorkspaces/piazza_downloads/stats/cs231a/winter14/top_statistics_student.csv' % os.getenv('HOME')

if __name__ == '__main__':
  reader = csv.DictReader(open(stats_file,'r'))
  ts = [float(row['Weighted Out Degree']) for row in reader]
  if len(ts)>2:
      if ts[0] != 0:
        ts0 = [0] + ts
      else:
        ts0 = ts
      diffs = np.diff(ts0).tolist()
      change_pt_model = ChangePointModel()
      #cusum_points = change_pt_model.compute_cusum_ts(diffs)
      #print(cusum_points)
      change_pt_model.run(diffs)
      print('Change pts: %s' % change_pt_model.change_intervals)
      change_pt_model.plot(diffs)
      print('Indices: %s' % change_pt_model.indices)
      #stats_file.plot(ts,'../figures/'+course+'/'+'changepoint_'+'outdeg'+course_dir+'.png','Weighted Out Degree')
    