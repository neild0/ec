import pybiopax

class BioChemReaction:
    def __init__(self, reaction):
        self.reactants = [Molecule(x.standard_name) if type(x) != str else Molecule(x) for x in reaction.controlled.left]
        self.products = [Molecule(x.standard_name) if type(x) != str else Molecule(x) for x in reaction.controlled.right]
        self.protein = reaction.standard_name
        self.reversible = False
    def __str__(self):
        reactants_str, products_str = " + ".join([str(x) for x in self.reactants]), " + ".join([str(x) for x in self.products])
        return f"{reactants_str} -> {products_str} ({self.protein})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.reactants == other.reactants and self.products == other.products and self.protein == other.protein and self.reversible == other.reversible

    def __hash__(self):
        return hash((tuple(self.reactants), tuple(self.products), self.protein, self.reversible))

class Molecule:
    def __init__ (self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.name == other.name
class BioChemReactionSet:
    def __init__(self, reactions):
        self.reactions = reactions

class Protein:
    def __init__(self, name, reactions=None):
        self.name = name
        self.reactions = reactions
        self.reactants = [x.reactants for x in reactions] if reactions else []
        self.products = [x.products for x in reactions] if reactions else []

    def add_reaction(self, reaction):
        self.reactions.append(reaction)
        self.reactants.append(reaction.reactants)
        self.products.append(reaction.products)


class ProteinSet:
    def __init__(self, proteins = None):
        self.proteins = proteins if proteins else []

    def add_protein(self, protein):
        self.proteins.append(protein)

    def add_reaction(self, reaction):
        for protein in self.proteins:
            if protein.name == reaction.protein:
                protein.add_reaction(reaction)
                break
        else:
            self.add_protein(Protein(reaction.protein, [reaction]))