import numpy as np
import scipy.stats as stats

class Dogs:
    data = []
    y = []
    n_dogs = 0
    n_trials = 0
    num_success = []
    num_failure = []
    accepted_alpha = []
    accepted_beta = []
    def __init__(self, data):
        self.data = data
        self.n_dogs, self.n_trials = data.shape
        self.flip_data()
        self.calculate_number_of_success_failure()

    def show_data(self):
        print self.data

    def flip_data(self):
        self.y = 1 - self.data

    def calculate_number_of_success_failure(self):
        self.num_success = np.zeros((self.n_dogs, self.n_trials), dtype=np.int32) # No shock
        self.num_failure = np.zeros((self.n_dogs, self.n_trials), dtype=np.int32)
        for d in range(self.n_dogs):
            self.num_success[d,0] = 0
            self.num_failure[d,0] = 0
            for t in range(1, self.n_trials):
                for i in range(0, t):
                    self.num_success[d, t] = self.num_success[d, t] + self.data[d, i]
                self.num_failure[d, t] = t - self.num_success[d, t]

    def calculate_likelihood(self, alpha, beta):
        # num_success = np.zeros((self.n_dogs, self.n_trials), dtype=np.int32) # No shock
        # num_failure = np.zeros((self.n_dogs, self.n_trials), dtype=np.int32)
        # for d in range(self.n_dogs):
        #     num_success[d,0] = 0
        #     num_failure[d,0] = 0
        #     for t in range(1, self.n_trials):
        #         for i in range(0, t):
        #             num_success[d, t] = num_success[d, t] + self.data[d, i]
        #         num_failure[d, t] = t - num_success[d, t]

        p_log = np.zeros((self.n_dogs, self.n_trials), dtype=np.float64)
        p = np.zeros((self.n_dogs, self.n_trials), dtype=np.float64)

        # for d in range(self.n_dogs):
        #     for t in range(self.n_trials):
        #         p_log[d][t] = alpha * self.num_success[d][t] + beta * self.num_failure[d][t]

        p_log = alpha * self.num_success + beta * self.num_failure

        # p = np.exp(p_log)
        # prob = np.zeros((self.n_dogs, self.n_trials), dtype=np.float64)
        #
        # for d in range(self.n_dogs):
        #     for t in range(self.n_trials):
        #         prob[d][t] = stats.bernoulli(p[d][t]).pmf(self.y[d][t])

        # likelihood = prob.prod()
        # likelihood = p.prod()
        likelihood = np.exp(np.sum(p_log))
        # print likelihood
        return likelihood

    def mcmc_sampler(self, alpha_init, beta_init, iteration=5):

        alpha_prev = alpha_init
        beta_prev = beta_init
        n_accepted = 0
        n_rejected = 0
        accepted_alpha = [alpha_init]
        accepted_beta = [beta_init]
        burn_in = np.ceil(0.1 * iteration)


        for i in range(iteration):
            # loc specifies the mean, scale is the standard deviation
            alpha_new = - stats.expon.rvs(scale=.0005)
            beta_new = - stats.expon.rvs(scale=.0005)

            # Posterior Calculation
            likelihood_prev = self.calculate_likelihood(alpha_prev, beta_prev)
            likelihood_new = self.calculate_likelihood(alpha_new, beta_new)

            alpha_prior_prev = stats.norm.pdf(alpha_prev)
            beta_prior_prev = stats.norm.pdf(beta_prev)

            alpha_prior_new = stats.norm.pdf(alpha_new)
            beta_prior_new = stats.norm.pdf(beta_new)

            posterior_prev = likelihood_prev * alpha_prior_prev * beta_prior_prev
            posterior_new = likelihood_new * alpha_prior_new * beta_prior_new

            # Proposal distribution pdf value
            proposal_prob_prev = stats.norm.pdf(alpha_prev) * stats.norm.pdf(beta_prev)
            proposal_prob_new = stats.norm.pdf(alpha_new) * stats.norm.pdf(beta_new)

            acceptance_ratio = min(1, (posterior_new * proposal_prob_prev) / (posterior_prev * proposal_prob_new))
            accept = np.random.rand() < acceptance_ratio

            if accept and (i > burn_in):
                alpha_prev = alpha_new
                beta_prev = beta_new

                n_accepted += 1
                accepted_alpha.append(alpha_new)
                accepted_beta.append(beta_new)
                # print "---"
                # print n_accepted
                # print i

            else:
                n_rejected += 1

        print "***"
        print n_accepted
        print n_rejected
        # print np.average(accepted_alpha)
        # print np.average(accepted_beta)
        # print "***"
        self.accepted_alpha = accepted_alpha
        self.accepted_beta = accepted_beta
        return (accepted_alpha, accepted_beta)

    def compute_posterior(self, alpha, beta, prior=None):
        likelihood = self.calculate_likelihood(alpha, beta)

        if prior:
            posterior = likelihood * prior
        else:
            alpha_prior = stats.norm.pdf(alpha)
            beta_prior = stats.norm.pdf(beta)
            posterior = likelihood * alpha_prior * beta_prior

        # print posterior
        return posterior

    def predict(self):

        num_success = 10
        num_failure = 4
        prediction = []

        for _ in range(0,11):
            pred = 0
            posterior = None
            for i in range (0, len(self.accepted_alpha)):
                log_p = self.accepted_alpha[i] * num_success + self.accepted_beta[i] * num_failure
                p = np.exp(log_p)
                posterior = self.compute_posterior(self.accepted_alpha[i], self.accepted_beta[i])
                prod = p * posterior
                pred = pred + prod

            if pred > 0.5:
                num_failure += 1
            else:
                num_success += 1
            prediction.append(pred)

        print num_success
        print num_failure
        print prediction


data = (0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0,
           0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1,
           0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
n_dogs = 30
n_trial = 25
data = np.array(data).reshape(n_dogs, n_trial)

d = Dogs(data)
# d.calculate_likelihood(-0.00001, -0.00001)
d.mcmc_sampler(-.00001, -.00001, 1000)

d.predict()
