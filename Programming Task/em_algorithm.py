from enum import Enum
import math
import pprint


class Dist(Enum):
    Initialisation = 0
    Transition = 1
    Emission = 2


class EMAlgorithm:
    def __init__(self, data, initialisation, transition, emission):
        self._data = data
        self._λ = {
            Dist.Initialisation: initialisation,   # Pi
            Dist.Transition: transition,           # A
            Dist.Emission: emission                # B
        }

    def debug_distributions(self):
        assert (abs(1 - sum(self._λ[Dist.Initialisation].values())) <= 0.001)

        for i in self._λ[Dist.Transition]:
            assert (abs(1 - sum(self._λ[Dist.Transition][i].values())) <= 0.001)

        for j in self._λ[Dist.Emission]:
            assert (abs(1 - sum(self._λ[Dist.Emission][j].values())) <= 0.001)

    def _generate_alpha(self, episode):
        alpha = []

        for emission in episode:
            emission = emission['reward']

            alpha_step = {}

            if len(alpha) == 0:
                # Initialisation step..
                for cell in self._λ[Dist.Initialisation]:
                    alpha_step[cell] = self._λ[Dist.Initialisation][cell] * self._λ[Dist.Emission][cell][emission]

            else:
                # Transition step..
                for destination in self._λ[Dist.Emission]:
                    sum_of_probs = 0

                    # This is transition step- previous_cell is the cell we are moving FROM
                    for origin in self._λ[Dist.Transition]:
                        sum_of_probs += alpha[-1][origin] * self._λ[Dist.Transition][origin][destination]

                    # Coord of NEW step..
                    alpha_step[destination] = self._λ[Dist.Emission][destination][emission] * sum_of_probs

            alpha.append(alpha_step)
        return alpha

    def _generate_beta(self, episode):
        size = int(math.sqrt(len(self._λ[Dist.Initialisation])))
        beta = [{(math.floor(x / size), x % size): 1 for x in range(size ** 2)}]

        for emission in reversed(episode):
            emission = emission["reward"]

            beta.insert(0, {})
            for origin in self._λ[Dist.Transition]:
                beta[0][origin] = 0
                for destination in self._λ[Dist.Transition][origin]:
                    beta[0][origin] += beta[1][destination] * self._λ[Dist.Transition][origin][destination] * self._λ[Dist.Emission][destination][emission]

        beta.pop(0)
        return beta

    @staticmethod
    def _generate_gamma(alpha, beta):
        gamma = []
        for index, beta_time_step in enumerate(beta):
            gamma_step = {}

            alpha_time_step = alpha[index]
            for coord in beta_time_step:
                numerator = alpha[index][coord] * beta[index][coord]
                denominator = 0
                for state in alpha_time_step:
                    denominator += alpha_time_step[state] * beta_time_step[state]

                if numerator == 0 and denominator == 0:
                    gamma_step[coord] = 0
                else:
                    gamma_step[coord] = numerator / denominator
            gamma.append(gamma_step)
        return gamma

    def _generate_xi(self, episode, alpha, beta):
        xi = []
        transition = self._λ[Dist.Transition]

        for timestep in range(len(episode) - 1):
            xi.append({})

            sum_over_ij = 0
            for origin in transition:
                xi[timestep][origin] = {}
                for destination in transition[origin]:
                    yt = episode[timestep+1]["reward"]
                    xi[timestep][origin][destination] = alpha[timestep][origin] * self._λ[Dist.Transition][origin][destination] * beta[timestep + 1][destination] * self._λ[Dist.Emission][destination][yt]
                    sum_over_ij += xi[timestep][origin][destination]

            for origin in transition:
                for destination in transition[origin]:
                    xi[timestep][origin][destination] /= sum_over_ij

        return xi

    @staticmethod
    def _indicator(yt, vk):
        if yt == vk:
            return 1
        return 0

    def _update_initialisation(self, gammas):
        for coord in self._λ[Dist.Initialisation]:
            self._λ[Dist.Initialisation][coord] = 0
            for gamma in gammas:
                self._λ[Dist.Initialisation][coord] += gamma[0][coord]
            self._λ[Dist.Initialisation][coord] /= len(gammas)

    def _update_transition(self, gammas, xis):
        transition = self._λ[Dist.Transition]

        for origin in transition:
            gammas_sum = 0
            for gamma in gammas:
                gamma_sum = 0
                for time in range(len(gamma)-1):
                    gamma_sum += gamma[time][origin]
                gammas_sum += gamma_sum / (len(gamma) - 1)

            for destination in transition[origin]:
                xis_sum = 0
                for xi in xis:
                    xi_sum = 0
                    for time in range(len(xi)):
                        xi_sum += xi[time][origin][destination]
                    xis_sum += xi_sum / (len(xi))

                if gammas_sum == 0:
                    transition[origin][destination] = 0
                else:
                    transition[origin][destination] = xis_sum / gammas_sum

    def _update_emission(self, gammas):
        emission = self._λ[Dist.Emission]

        for cell in emission:
            for value in emission[cell]:
                numerator = 0
                denominator = 0

                for index, episode in enumerate(self._data):
                    gamma = gammas[index]

                    for time_period, reward in enumerate(episode):
                        gamma_val = gamma[time_period][cell] / len(gammas)

                        numerator += gamma_val * self._indicator(value, reward["reward"])
                        denominator += gamma_val

                if denominator == 0:
                    emission[cell][value] = 0
                else:
                    emission[cell][value] = numerator / denominator

    def _log_likelihood(self):
        log_likelihood = 0

        for episode in self._data:
            likelihood = 0

            alpha = self._generate_alpha(episode)
            for cell in alpha[-1]:
                likelihood += alpha[-1][cell]

            log_likelihood += math.log(likelihood)

        return log_likelihood

    def _iterate(self):
        gammas = []
        xis = []

        for episode in self._data:
            alpha = self._generate_alpha(episode)
            beta = self._generate_beta(episode)

            gamma = self._generate_gamma(alpha, beta)
            gammas.append(gamma)

            xi = self._generate_xi(episode, alpha, beta)
            xis.append(xi)

        self._update_initialisation(gammas)

        self._update_transition(gammas, xis)

        self._update_emission(gammas)

    def print_params(self):
        print("")
        print("Initialisation: ")
        for origin, probability in self._λ[Dist.Initialisation].items():
            print("P(h1 = " + str(origin) + ") = " + str(round(probability, 3)))
        # Aim: 0.0625, with rounding errors?

        print("\nTransition: ")
        for origin, probabilities in self._λ[Dist.Transition].items():
            for destination, probability in probabilities.items():
                print("P(ht+1 = " + str(destination) + " | ht = " + str(origin) + ") = " + str(round(probability, 3)))
            print("")
        # Aim: 0.0625, with rounding errors?

        print("\nEmission: ")
        for origin, probabilities in self._λ[Dist.Emission].items():
            for emission, probability in probabilities.items():
                pad = ""
                if emission >= 0:
                    pad = " "
                print("P(vt = " + pad + str(emission) + " | ht = " + str(origin) + ") = " + str(round(probability, 3)))
            print("")
        # Aim:
        #  0: 20 / 49
        # -1: 20 / 49
        #  1:  9 / 49
        print("")

    def run(self):
        log_likelihood = self._log_likelihood()
        self.print_params()
        print("Log-Likelihoods:")
        print(round(log_likelihood, 3))
        i = 1
        while True:
            self.debug_distributions()
            # print("Iteration", i, ":")
            self._iterate()
            # N.B. PRINT ALL PARAMETERS

            new_likelihood = self._log_likelihood()  # Expecting: -51 for log-likelihood?
            print(round(new_likelihood, 3))  # N.B. PRINT LOG LIKELIHOOD TO STANDARD OUTPUT

            if abs(log_likelihood - new_likelihood) < 0.01:
                # Stop iteration if log-likelihood is less than 0.01 changed compared to previous iteration..
                self.print_params()
                break
            log_likelihood = new_likelihood
            i += 1
            #print("\n\n")
