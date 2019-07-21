
## Elo, Glicko and Glicko2 implementations in Python 3

### Features
- [x] Perf-rating calculator ("algorithm of 400" and FIDE)
- [x] Elo-per-pawn approximation
- [x] Elo implementation (to be improved)
- [ ] Glicko implementation
- [ ] Glicko2 implementation

### "Documentation"

The following is an incomplete function/class listing:
```
float perf_approx(total_rating: float, wins: int, losses: int, draws: int)
float perf_fide(mean_rating: float, score: float, n_games: int)
float elo_per_pawn(mean_rating: float)
```

```
abstract class Distribution:
	__init__(mean = 0.0, variance = 1.0)

	property mean: float
	property variance: float

	float pdf(x: float)
	float cdf(x: float)

class NormalDistribution (Distribution)

class LogisticDistribution (Distribution):
	property scale: float
	
	float quantile(p: float)

```

```
class Rating:
	property value: float

class GlickoRating (Rating):
	property rd: float (rating deviation)
	
	tuple(min: float, max: float) confidence_interval()


class Glicko2Rating (GlickoRating):
	property tau: float (rating volatility)
```

```
abstract class RatingSystem:
	property dist: Distribution

	float expected(a: Rating, b: Rating)
	static float adjustment(expected score: float, actual score: float, number of games: int)

class EloRatingSystem (RatingSystem)
class GlickoRatingSystem (RatingSystem)
class Glicko2RatingSystem (RatingSystem)

```

### Resources
1. [Mathematical details of Elo](https://en.wikipedia.org/wiki/Elo_rating_system#Mathematical_details)
1. [Useful Elo calculator / some other info](https://wismuth.com/elo/calculator.html)
2. [Glicko](http://www.glicko.net/glicko/glicko.pdf)
3. [Glicko2](http://www.glicko.net/glicko/glicko2.pdf)

