from math import exp, pi, sqrt, erf, log


def perf_approx(total_rating: float, wins: int, losses: int, draws: int):
	"""Evaluates performance rating.
	Uses the "algorithm of 400" approximation.
	:param total_rating: total rating of tournament
	:param wins: number of wins
	:param losses: number of losses
	:param draws: number of draws
	:return: performance rating value
	"""
	return (total_rating + 400 * (wins - losses)) / (wins + losses + draws)


def perf_fide(mean_rating: float, score: float, n_games: int):
	"""Evaluates performance rating according to FIDE rules.
	Undefined behaviour if :param score: > :param n_games:.
	:param mean_rating: mean rating of all opponents
	:param score: score
	:param n_games: number of games played
	:return: performance rating value
	"""
	dp = [
		800, 677, 589, 538, 501, 470, 444, 422, 401, 383,
		366, 351, 336, 322, 309, 296, 284, 273, 262, 251,
		240, 230, 220, 211, 202, 193, 184, 175, 166, 158,
		149, 141, 133, 125, 117, 110, 102, 95,  87,  80,
		72,  65,  57,  50,  43,  36,  29,  21,  14,  7,
		0
	]

	p = int((score / n_games) * 100)
	sign = 1

	if p > 50:
		p = 100 - p
		sign = -1

	return mean_rating + sign * dp[p]


def elo_per_pawn(mean_rating: float):
	"""
	Estimate of elo rating per pawn from mean rating of two players
	:param mean_rating: mean rating of two players
	:return: elo rating per pawn
	"""
	return exp(mean_rating / 1020) * 26.59


class Distribution:
	def __init__(self, mean: float, variance: float):
		self._mean = mean
		self._variance = variance

	@property
	def mean(self):
		return self._mean

	@property
	def variance(self):
		return self._variance

	@mean.setter
	def mean(self, mean):
		self._mean = mean

	@variance.setter
	def variance(self, variance):
		self._variance = variance

	def pdf(self, x):
		raise NotImplementedError

	def cdf(self, x):
		raise NotImplementedError


class NormalDistribution(Distribution):
	def __init__(self, mean: float = 0.0, variance: float = 1.0):
		super().__init__(mean, variance)

	def pdf(self, x):
		"""
		Probability density function
		"""
		a = sqrt(2. * pi * self.variance)
		b = -(x - self.mean) / (2 * self.variance)
		return exp(b) / a

	def cdf(self, x):
		"""
		Cumulative distribution function
		"""
		a = x - self.mean / (sqrt(2 * self.variance))
		return 0.5 + 0.5 * erf(a)


class LogisticDistribution(Distribution):
	def __init__(self, mean: float = 0.0, scale: float = 1.0):
		super().__init__(mean, ((scale * pi) ** 2) / 3)
		self._scale = scale

	@property
	def scale(self):
		return self._scale

	@scale.setter
	def scale(self, scale):
		self._scale = scale
		self._variance = ((scale * pi) ** 2) / 3

	@property
	def variance(self):
		return self._variance

	@variance.setter
	def variance(self, variance):
		self._variance = variance
		self._scale = sqrt((3 * variance) / pi ** 2)

	def pdf(self, x):
		"""
		Probability density function,
		defined as:
			a(x; μ, s) = exp( -(x - μ) / s )
			f(x; s) = a(x) / (s . a(x))
		"""
		a = exp(-(x - self.mean) / self.scale)
		return a / (self.scale * (1 + a) ** 2)

	def cdf(self, x):
		"""
		Cumulative distribution function,
		defined as:
			F(x; μ, s) = 1 / (1 + exp( -(x - μ) / s ))
		"""
		a = exp(-(x - self.mean) / self.scale)
		return 1. / (1. + a)

	def quantile(self, p):
		"""
		Inverse of the cumulative distribution function (a.k.a. quantile function),
		defined as:
			Q (p; μ, s) = μ + s.ln (p / (1 - p))
		"""
		return self.mean + self.scale * log(p / (1. - p))


class Rating:
	def __init__(self, value: float):
		self._value = value

	@property
	def value(self):
		return self._value

	@value.setter
	def value(self, value):
		self._value = value


class GlickoRating(Rating):
	def __init__(self, value: float, rd: float = 0):
		super().__init__(value)
		self._rd = rd

	@property
	def rd(self):
		"""Rating deviation"""
		return self._rd

	@rd.setter
	def rd(self, rd):
		self._rd = rd

	def confidence_interval(self):
		"""95% confidence interval"""
		d = 2 * self.rd
		return self.value - d, self.value + d


class Glicko2Rating(GlickoRating):
	def __init__(self, value: float, rd: float = 0, tau: float = 0):
		super().__init__(value, rd)
		self._tau = tau

	@property
	def tau(self):
		"""Rating volatility"""
		return self._tau

	@tau.setter
	def tau(self, tau):
		self._tau = tau


class RatingSystem:
	def __init__(self):
		self._dist = None

	@property
	def dist(self):
		return self._dist

	@dist.setter
	def dist(self, dist: Distribution):
		self._dist = dist

	def expected(self, a: Rating, b: Rating):
		raise NotImplementedError

	@staticmethod
	def adjustment(ex: float, score: int, k: int = 32):
		raise NotImplementedError


class EloRatingSystem(RatingSystem):
	"""
	'Q' is the scale of the distribution.
	log (10) is required due to LogisticDistribution being in base e, rather than base 10.
	"""
	Q = 400. / log(10)

	def __init__(self):
		super().__init__()
		self.dist = LogisticDistribution(0., self.Q)

	def expected(self, a: Rating, b: Rating):
		"""Evaluate the expected score of player A versus player B
		:param a: rating of player A
		:param b: rating of player B
		:return: expected score
		"""
		self.dist.mean = b.value
		return self.dist.cdf(a.value)

	@staticmethod
	def adjustment(ex: float, score: int, k: int = 32):
		"""
		Calculate the rating adjustment according to expected and actual scores
		:param ex: expected score of player
		:param score: actual score of player
		:param k: K factor (default: 32)
		:return: rating adjustment
		"""
		return k * (score - ex)


class GlickoRatingSystem(RatingSystem):
	pass


class Glicko2RatingSystem(RatingSystem):
	pass


















