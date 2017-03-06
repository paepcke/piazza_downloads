import numpy as np
import spc
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import csv

from constants import *

'''
Bootstrap implementation based on www.variation.com/cpa/tech/changepoint.html
'''

class ChangePointModel(object):
    def __init__(self):
        self.change_intervals = set()
        self.points = []

    def compute_cusum_ts(self, ts):
        """ Compute the Cumulative Sum at each point 't' of the time series. """
        mean = np.mean(ts)
        cusums = np.zeros(len(ts))
        cusums[0] = (ts[0] - mean)
        for i in np.arange(1, len(ts)):
            cusums[i] = cusums[i - 1] + (ts[i] - mean)

        assert(np.isclose(cusums[-1], 0.0))
        return cusums

    def shuffle_timeseries(self, ts):
        """ Shuffle the time series. """
        return np.random.permutation(ts)

    def bootstrap(self, ts, name=None, B=1000,plot=False):
        # Generating a bootstrap sample
        permutations = np.vstack([self.shuffle_timeseries(ts) for i in np.arange(0, B)])

        # Calculating the bootstrap CUSUM
        bootstrap_cusum = np.vstack([self.compute_cusum_ts(p) for p in permutations])
        #print bootstrap_cusum

        # Calculate the maximum, minimum and difference of the bootstrap CUSUM
        # S0_max = np.amax(bootstrap_cusum, axis=1)
        # S0_min = np.amin(bootstrap_cusum, axis=1)
        # S0_diff = np.subtract(S0_max,S0_min)
        #print 'S0_diff',S0_diff

        original_cusum = self.compute_cusum_ts(ts)
        #print 'ORIGINAL :',original_cusum
        S_max = np.amax(original_cusum)
        S_min = np.amin(original_cusum)
        S_diff = np.subtract(S_max,S_min)
        #print 'S_diff',S_diff
        found_critical_point=False
        num_small_bootstrap_diff = 0
        for cusum in bootstrap_cusum:
            S0_max = np.amax(cusum, axis=0)
            S0_min = np.amax(cusum, axis=0)
            S0_diff = S0_max - S0_min
            if S0_diff < S_diff:
               num_small_bootstrap_diff += 1
        if 100*num_small_bootstrap_diff/float(1000) >= 95: 
            found_critical_point=True

        if plot:
            plt.clf()
            best_bootstraps = [bootstrap_cusum[i] for i in S0_diff.argsort()[-5:][::-1]]
            i=1
            colors = ['r','y','m','k','c']
            for b in best_bootstraps:
                i+=1
                plt.plot(np.array(range(1,len(best_bootstraps[0])+1)),np.array(b),'-o',color=colors[i-2],label='bootstrap'+str(i-1))

            plt.plot(range(1,len(best_bootstraps[0])+1),ts ,color = 'g', linewidth='4', label = 'Weighted out degrees')    
            plt.plot(range(1,len(best_bootstraps[0])+1),original_cusum,color='b',linewidth='4',label='Original CUSUM')
            
            ax = plt.gca()
            # Shrink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width, box.height * 0.9])

            # Put a legend below current axis
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                      fancybox=True, shadow=True, ncol=4, fontsize=11)

            #plt.legend(loc='best')
            plt.title(name, fontsize=40)
            ax.tick_params(labelsize=30)
            print '../figures/'+name.split('/')[0]+'/cusum_'+name.split('/')[1]+'.png'
            #plt.show()
            plt.savefig('../figures/'+name.split('/')[0]+'/cusum_'+name.split('/')[1]+'.png')
        print original_cusum
        max_cusum_abs_value = max(abs(S_max), abs(S_min))
        return S0_diff,S_diff,(abs(original_cusum).tolist()).index(max_cusum_abs_value),found_critical_point

    def confidence(self, S0_diff, S_diff):
        # Determine the number of samples for which the bootstrap difference S0diff 
        # is less than the original difference Sdiff
        X = np.sum((S0_diff[i]<=S_diff) for i in range(len(S0_diff)))
        return X*100/float(1000)

    #def plot_bootstrap_histogram():

    def mean_square_error(self, ts, m):
        X1 = np.sum([ts[i] for i in range(m)])/float(m)
        X2 = np.sum([ts[i] for i in range(m,len(ts))])/float(len(ts)-m)

        return np.sum([(ts[i]-X1)*(ts[i]-X1) for i in range(m)]) + np.sum([(ts[j]-X2)*(ts[j]-X2) for j in range(m,len(ts))])

    def estimate_best_m(self, ts):
        return np.argmin([self.mean_square_error(ts,m) for m in range(1,len(ts))])

    def estimate_best_m2(self,ts,S_max,S_min):
        max_cusum_abs_value = max(abs(S_max), abs(S_min))
        print ts
        return ts.index(max_cusum_abs_value)

    def run(self, ts, name=None, B=1000, plot=False):
        N = len(ts)

        if len(ts)>1:
            S0_diff,S_diff,best_m,found_critical_point = self.bootstrap(ts,name=name, B=B, plot=plot)
            #conf  = self.confidence(S0_diff,S_diff)
            if found_critical_point: 
                self.points.append(ts[best_m])
            #print 'ts = ', ts
            #best_m = self.estimate_best_m(ts)
            #best_m = self.estimate_best_m2(ts, S_max, S_min)
            # print  'best_m:',best_m
            # print 'elem  :',ts[best_m]
            
           # if conf > 95:
                #print 'conf = ',conf
                #self.change_intervals.add(ts[best_m])
            #print self.change_intervals
            self.run(ts[:best_m],B)
            self.run(ts[best_m+1:],B)

    def normalize(self,ts):
        return [(x-min(ts))/(max(ts)-min(ts)) for x in ts]

    def plot(self,ts, plot_name = None, parameter=None):
        import matplotlib.pyplot as plt
        weeks = range(1,len(ts)+1)
        #self.indices = [ts.index(list(self.change_intervals)[j]) for j in range(len(self.change_intervals)) if ts.index(list(self.change_intervals)[j])!=weeks[len(weeks)-1]]
        #self.indices = [0,2,4,7,10]
        self.indices = [ts.index(self.points[j]) for j in range(len(self.points))]
        plt.figure()
        plt.xlabel('Week')
        plt.ylabel(parameter)
        ax=plt.gca()
        ax.set_axis_bgcolor('yellow')
        plt.title('Change point detection '+plot_name.split('/')[2] + plot_name.split('_')[-1].split('.png')[0])

        normalized_ts = self.normalize(ts)
        print normalized_ts
        #for index in sorted(self.indices):
           # plt.axvspan(index,index+1,ymin=normalized_ts[index]+0.3,ymax=normalized_ts[index+1]-0.3,facecolor='cyan', alpha=0.9, linewidth='0.0')
        plt.axvspan(0, 2, ymin=0.2,ymax=0.4,facecolor='cyan', alpha=1, linewidth='0.0')
        plt.axvspan(2, 4, ymin=0.3,ymax=0.5,facecolor='cyan', alpha=1, linewidth='0.0')
        plt.axvspan(4, 7, ymin=0.4,ymax=0.85,facecolor='cyan', alpha=1, linewidth='0.0')
        plt.axvspan(7, 10, ymin=0.3,ymax=0.65,facecolor='cyan', alpha=1, linewidth='0.0')
        #plt.axvspan(7, 8, ymin=0.3,ymax=0.63,facecolor='cyan', alpha=0.9, linewidth='0.0')
        plt.axvspan(10, 12, ymin=0.3,ymax=0.5,facecolor='cyan', alpha=1, linewidth='0.0')
        
        #green_patch = mpatches.Patch(color='cyan', label='>95% confidence change')
        #plt.legend(loc='best',handles=[green_patch])

        # Creating control chart
        cc = spc.Spc(ts, spc.CHART_X_MR_X)
        cc.get_chart()

        if plot_name: plt.savefig(plot_name)
        else: plt.show()


if __name__ == "__main__":
    '''
    ts = [0.0013316809193246381, 0.005478151755720595, 0.005588738892689889, 0.00658393992617357,
          0.007088258402213599, 0.007021522084785884, 0.007048596731015847, 0.007719706402863562,
          0.007805863541411589, 0.00787893333851693, 0.00779095482226361, 0.0077741221689227894,
          0.007966075694506278, 0.0033839897207213697]
    '''
    file = '../stats/cs229/fall15/top_statistics_student.csv'
    reader = csv.DictReader(open(file,'r'))
    ts = [float(row['Weighted Out Degree']) for row in reader]
    if ts[0] != 0:
        ts0 = [0] + ts
    else:
        ts0 = ts
    diffs = np.diff(ts0).tolist()
    model = ChangePointModel()
    model.run(diffs)
    #model.run(ts,name='cs221fallsomething',plot=True)
    model.plot(diffs,'../figures/cs229/'+'changepoint_'+'outdegfall15.png','Weighted Out Degree')
    print sorted(model.indices)
