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
