"""Main file of the python starter, code and send your solution in this module
"""

from src.car import Car
from src.car import RandomCar
from src.carScoreView import CarScoreView
from ranking import Ranking
from ranking import DENSE

import ujson
import httplib2
from random import random
from random import shuffle
from random import randint

team = 'RED'  # RED, YELLOW, BLUE, GREEN, ORANGE, PURPLE
host = "http://genetic-car.herokuapp.com"
#host = "http://localhost:9000"


def run():
    doMyAlgo()


def evaluate(carsView):
    """This will send your cars to the competition server and give to each of them
    a core. Then the best of those cars will be considered as your champion, the
    one which will be match against other teams. Those scores will be returned.
    """
    url = host + "/simulation/evaluate/" + team
    h = httplib2.Http(".cache")
    resp_headers, content = h.request(
        url,
        "POST",
        ujson.dumps(carsView),
        headers={'content-type': 'application/json'}
    )
    result = ujson.decode(content)
    return [CarScoreView(car_view, res["score"])
            for car_view, res in zip(carsView, result)]


def cross(parent1, parent2):
    child1 = Car()
    child2 = Car()
    child1.coords = [gene for gene in parent1.coords]
    child2.coords = [gene for gene in parent2.coords]
    for i in range(len(child1.coords)):
        if random() >= 0.5:
            child1.coords[i], child2.coords[
                i] = child2.coords[i], child1.coords[i]
    return (child1, child2)



def mutate(parent):
    genes = parent.coords
    random_car = RandomCar()
    random_gene = randint(0, len(genes) - 1)
    random_allele = random_car.coords[random_gene]
    mutant = Car()
    mutant.coords = [gene for gene in genes]
    mutant.coords[random_gene] = random_allele
    return mutant


def select(cars, carScores):
    scored_cars = [[car, carScore.score]
                   for car, carScore in zip(cars, carScores)]
    scored_cars.sort(cmp=lambda x, y: cmp(y[1], x[1]))
    rankings = []
    for rank, _ in Ranking([score[1] for score in scored_cars], strategy=DENSE):
        rankings += [rank]
    ranks = [len(rankings) - rank for rank in rankings]
    prob = [float(rank) / sum(ranks) for rank in ranks]
    for i in range(1, len(prob)):
        prob[i] += prob[i - 1]

    parents = []
    for i in range(int(len(prob) * 0.8)):
        index = 0
        rand = random()
        while prob[index] < rand:
            index += 1
        parents.append(scored_cars[index][0])
    return parents


def doMyAlgo():
    cars = [RandomCar() for i in range(20)]
    carScores = evaluate([car.to_carView() for car in cars])

    # Here comes your algo
    ##########################################################################
    for step in range(100):
        parents = select(cars, carScores)
        shuffle(parents)
        children = []
        for i in range(0, len(parents) - 1, 2):
            parent1, parent2 = parents[i], parents[i + 1]
            child1, child2 = cross(parent1, parent2)
            children.append(child1)
            children.append(child2)

        mutant = mutate(parents[0])
        children.append(mutant)
        champion = max(carScores, key=lambda carScore: carScore.score)
        champion = [Car(champion.car)]
        children_scores = evaluate(
            [car.to_carView() for car in children + champion])
        carScores += children_scores
        carScores.sort(key=lambda carScore: carScore.score, reverse=True)
        cars = [Car(carscoreview.car) for carscoreview in carScores[:20]]
    ##########################################################################

    champion = max(carScores, key=lambda carScore: carScore.score)
    print "Mon champion est {}".format(champion)

if __name__ == '__main__':
    run()
