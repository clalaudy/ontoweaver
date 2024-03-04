'''
Pre-processing of ontologies in order to be compatible with the requierements of Biocypher.

python3 -m preprocess_ontology <ontology_directory> <ontology_to_be_transformed>.owl
>> creates 
	- a new Biocypher compatible ontology, in <ontology_directory> named bc_<ontology_to_be_transformed>.owl
	- a 'bc_classes_mapping.json' file containing the mapping 
		between classes from <ontology_to_be_transformed>.owl and classes from bc_<ontology_to_be_transformed>.owl

Each element of bc_classes_mapping.json fiile is a json input with the folloging information:

<initial_classe_IRI in ontology>: {
    "labels": [
	    <list of the labels in the initial ontology>
        ],
	"bc_label": "<label in bc_ontology>"
}


'''

import owlready2 as owl
import types
import json
import copy

chars_to_be_removed = [' ', "%", "-"]
chars_to_be_replaced = ["_"]

def remove_characters(s, list_c):
	for c in list_c:
		s = s.replace(c, "")
	return s

def replace_underscore(s):
	p = s.find("_")
	while p>=0:
		c = s[p+1]
		s2 = s[:p]+c.upper()
		if len(s)>=p+1:
			s2=s2+s[p+2:]
		s = s2
		p = s.find("_")
	return s


def get_label_from_iri(iri):
	if iri.rfind("#")>0:
		return iri[iri.rfind("#")+1:]
	elif iri.rfind("/")>0:
		return iri[iri.rfind("/")+1:]
	else:
		return iri


def to_bc_ontology(ontology_path, ontology_file):
	path = "".join(['file://',ontology_path, ontology_file])
	print("Loading ontology \n"+path)
	onto = owl.get_ontology("".join(['file://',ontology_path, ontology_file])).load()

	translation_dict = {}

	with onto:
		thing_label = owl.Thing.label
		#print("\nThing label =", thing_label, type(thing_label))
		if not thing_label:
			thing_label = ["Thing"]
			owl.Thing.label = thing_label
		#print("Thing new label =", owl.Thing.label)

		for c in onto.classes():
			#print(c)
			old_labels = c.label

			# labels = [l for l in c.label]
			# for l in labels:
			# 	new_label = remove_characters(l, chars_to_be_removed)#.lower()
			# 	new_label = replace_underscore(new_label)
			# 	new_label = new_label.capitalize()
			# 	c.label.append(new_label)
			
			# new_name = remove_characters(c.iri, chars_to_be_removed)
			# new_name = replace_underscore(new_name)
			# new_name = new_name.capitalize()
			if len(c.label)>0:
				new_label = c.label[0]
			else:
				new_label = get_label_from_iri(c.iri)#.lower()
			new_label = remove_characters(new_label, chars_to_be_removed)#.lower()
			new_label = replace_underscore(new_label)
			new_label = new_label[0].lower()+new_label[1:]
			c.label = []
			c.label.append(new_label)

			labels = c.label
			translation_dict[c.iri] = {
										#"class": c.iri,
										"labels": old_labels,
										#"bc_class": new_name,
										"bc_label": new_label
										}
			parents = c.is_a
			if parents == [owl.Thing]:
				with onto:
					bc_root_class = types.new_class("BcRootClass", (owl.Thing,)) 
					bc_root_class.label.append("BcRootClass")
					c.is_a = [bc_root_class]
			#print(c)

	with open("".join([ontology_path, "bc_classes_mapping.json"]), 'w') as fp:
		json.dump(translation_dict, fp, indent=4)

	onto.save("".join([ontology_path,"bc_", ontology_file]))


def update_initial_types_on_neo4j(type_mapping_file):
	pass


if __name__ == "__main__":
	import argparse
	p = argparse.ArgumentParser()
	p.add_argument("ontology_path")
	p.add_argument("ontology_file")
	args = p.parse_args()
	to_bc_ontology(args.ontology_path, args.ontology_file)

