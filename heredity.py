import csv
import itertools

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


# Main function for initial operations and data loading
def power_set(names):
    list1 = list(names)
    return [set(s) for s in itertools.chain.from_iterable(
        itertools.combinations(list1, i) for i in range(len(list1))
    )]


def conditional_probability(one_gene, two_gene, have_trait, people):
    probability = 1
    for person in people:
        # If the person's parent genes are available
        if people[person]['father'] or people[person]['mother']:

            # Finding parents and their gene copies
            father = people[person]['father']
            mother = people[person]['mother']
            father_gene_copy = 1 if father in one_gene else 2 if father in \
                                                                 two_gene else 0
            mother_gene_copy = 1 if mother in one_gene else 2 if mother in \
                                                                 two_gene else 0
            child_gene_copy = 1 if person in one_gene else 2 if person in \
                                                                two_gene else 0

            # Finding possibilities
            possibilities = []
            for i in range(3):
                for j in range(3):
                    if i + j == child_gene_copy:
                        possibilities.append((i, j))

            # Adding probabilities for each possibility
            """Considering this as an OR function"""
            temp = 0
            for poss in possibilities:
                i, j = poss
                if bool(i) == bool(father_gene_copy):
                    pr1 = 1 - PROBS["mutation"]
                else:
                    pr1 = PROBS["mutation"]
                if bool(j) == bool(mother_gene_copy):
                    pr2 = 1 - PROBS["mutation"]
                else:
                    pr2 = PROBS["mutation"]
                temp += (pr1 * pr2)

            """probability that a trait t and gene g together occur is: 
                p(g) * p(t)"""
            probability *= (temp * PROBS['trait'][1 if
            person in one_gene else 2 if person in two_gene else 0][True if
            person in have_trait else False])

        else:
            # If the parent genes are not available
            """probability that a trait t and gene g together occur is: 
                p(g) * p(t)"""
            probability *= (PROBS['gene'][1 if person in one_gene else
            2 if person in two_gene else 0] * PROBS['trait'][1 if
            person in one_gene else 2 if person in two_gene else 0][True if
            person in have_trait else False])

    # returning the joint probability
    return probability


def update(one_gene, two_gene, have_trait, joint_probability, probability):
    for person in probability:
        probability[person]['gene'][2 if person in two_gene else 1 if
        person in one_gene else 0] += joint_probability
        probability[person]['trait'][True if person in have_trait else False] \
            += joint_probability


def normalize(probability):
    for person in probability:
        for field in probability[person]:
            sum = 0
            for value in probability[person][field]:
                sum += probability[person][field][value]
            alpha = 1 / sum
            for value in probability[person][field]:
                probability[person][field][value] *= alpha


def main():
    people = load_data('family0.csv')
    # Setting probability for initial condition
    probability = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }}
        for person in people}

    # Saving the names of people
    names = set(people)

    # Looping for all those who have traits

    for have_trait in power_set(names):

        # Checking if the people violates the known information
        ignore = any(
            people[person]['trait'] is not None and
            people[person]['trait'] != (person in have_trait)
            for person in names)
        if ignore:
            continue

        # Considering every element to have single copy of gene
        for one_gene in power_set(names):
            # Considering every other element to have two copies of gene
            for two_gene in power_set(names - one_gene):
                # Finding the joint probability for the current scenario
                joint_probability = conditional_probability(one_gene, two_gene,
                                                            have_trait,
                                                            people)
                # Updating the probability distribution
                update(one_gene, two_gene, have_trait, joint_probability,
                       probability)

        # Normalizing the probability distribution
        normalize(probability)

    # Printing probability distribution for each person
    for person in probability:
        print(person)
        for field in probability[person]:
            print('\t{}'.format(field.capitalize()))
            for value in probability[person][field]:
                print(
                    '\t\t{}: {}'.format(value, round(probability[person][field][
                                                         value], 4)))
        print()


def load_data(file_name):
    data = dict()
    with open(file_name) as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['name']
            data[name] = {'name': name,
                          'mother': row['mother'],
                          'father': row['father'],
                          'trait': True if row['trait'] == '1' else False if
                          row['trait'] == '0' else None}
    return data


if __name__ == '__main__':
    main()
