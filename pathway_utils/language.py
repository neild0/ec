import pybiopax

model = pybiopax.model_from_pc_query('pathsfromto', ['MAP2K1'], ['MAPK1'])

for obj in model.objects:
    print(obj)