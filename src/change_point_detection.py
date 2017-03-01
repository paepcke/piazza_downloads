import numpy as np
import spc
import matplotlib.patches as mpatches

'''
Bootstrap implementation based on www.variation.com/cpa/tech/changepoint.html
'''

class ChangePointModel(object):
    def __init__(self):
        self.change_intervals = set()

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

    def bootstrap(self, ts, B=1000):
        # Generating a bootstrap sample
        permutations = np.vstack([self.shuffle_timeseries(ts) for i in np.arange(0, B)])
        # Calculating the bootstrap CUSUM
        bootstrap_cusum = np.vstack([self.compute_cusum_ts(p) for p in permutations])

        # Calculate the maximum, minimum and difference of the bootstrap CUSUM
        S0_max = np.amax(bootstrap_cusum, axis=1)
        S0_min = np.amin(bootstrap_cusum, axis=1)
        S0_diff = np.subtract(S0_max,S0_min)

        best_bootstraps = [bootstrap_cusum[i] for i in S0_diff.argsort()[-5:][::-1]]
        print len(best_bootstraps)

        original_cusum = self.compute_cusum_ts(ts)
        S_max = np.amax(original_cusum)
        S_min = np.amin(original_cusum)
        S_diff = np.subtract(S_max,S_min)

        return S0_diff,S_diff

    def confidence(self, S0_diff, S_diff):
        # Determine the number of samples for which the bootstrap difference S0diff 
        # is less than the original difference Sdiff
        X = np.sum((S0_diff[i]<=S_diff) for i in range(len(S0_diff)))
        return X*100/float(len(S0_diff))

    #def plot_bootstrap_histogram():

    def mean_square_error(self, ts, m):
        X1 = np.sum([ts[i] for i in range(m)])/float(m)
        X2 = np.sum([ts[i] for i in range(m,len(ts))])/float(len(ts)-m)

        return np.sum([(ts[i]-X1)*(ts[i]-X1) for i in range(m)]) + np.sum([(ts[i]-X2)*(ts[i]-X2) for i in range(m,len(ts))])

    def estimate_best_m(self, ts):
        return np.argmin([self.mean_square_error(ts,m) for m in range(1,len(ts))])

    def run(self, ts, B=1000):
        N = len(ts)

        if len(ts)>1:
            S0_diff,S_diff = self.bootstrap(ts,B)
            conf  = self.confidence(S0_diff,S_diff)

            best_m = self.estimate_best_m(ts)
            if conf > 99:
                self.change_intervals.add(ts[best_m])
            self.run(ts[:best_m+1],B)
            self.run(ts[best_m+1:],B)

    def plot(self,ts, plot_name = None, parameter=None):
        import matplotlib.pyplot as plt
        weeks = range(1,len(ts)+1)
        indices = [ts.index(list(self.change_intervals)[j]) for j in range(len(self.change_intervals)) if ts.index(list(self.change_intervals)[j])!=weeks[len(weeks)-1]]

        plt.figure()
        plt.xlabel('Week')
        plt.ylabel(parameter)
        plt.title('Change point detection '+plot_name.split('/')[2] + plot_name.split('_')[-1].split('.png')[0])

        for index in indices:
            plt.axvspan(index, index+1, facecolor='#2ca02c', alpha=0.5)
        
        green_patch = mpatches.Patch(color='#2ca02c', label='>99% confidence change')
        plt.legend(loc='best',handles=[green_patch])

        # Creating control chart
        cc = spc.Spc(ts, spc.CHART_X_MR_X)
        cc.get_chart()

        if plot_name: plt.savefig(plot_name)
        else: plt.show()


if __name__ == "__main__":
    ts = [0.0013316809193246381, 0.005478151755720595, 0.005588738892689889, 0.00658393992617357,
          0.007088258402213599, 0.007021522084785884, 0.007048596731015847, 0.007719706402863562,
          0.007805863541411589, 0.00787893333851693, 0.00779095482226361, 0.0077741221689227894,
          0.007966075694506278, 0.0033839897207213697]
    model = ChangePointModel()
    model.run(ts)
    model.plot(ts)