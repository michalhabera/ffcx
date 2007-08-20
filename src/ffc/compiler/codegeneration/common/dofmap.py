"Code generation for dof map"

__author__ = "Anders Logg (logg@simula.no)"
__date__ = "2007-01-24 -- 2007-05-08"
__copyright__ = "Copyright (C) 2007 Anders Logg"
__license__  = "GNU GPL version 3 or any later version"

# Modified by Kristian Oelgaard 2007

# FFC common modules
from ffc.common.utils import *

# FFC fem modules
from ffc.fem.finiteelement import *

# FFC codegeneration common modules
from ffc.compiler.codegeneration.common.utils import *

def generate_dof_map(dof_map, format):
    """Generate dictionary of code for the given dof map according to
    the given format"""

    code = {}

    # Generate code for signature
    code["signature"] = dof_map.signature()

    # Generate code for needs_mesh_entities
    code["needs_mesh_entities"] = __generate_needs_mesh_entities(dof_map, format)

    # Generate code for global_dimension
    code["global_dimension"] = __generate_global_dimension(dof_map, format)

    # Generate code for local_dimension
    code["local_dimension"] = "%d" % dof_map.local_dimension() 

    # Generate code for num_facet_dofs
    code["num_facet_dofs"] = "%d" % dof_map.num_facet_dofs()

    # Generate code for tabulate_dofs
    code["tabulate_dofs"] = __generate_tabulate_dofs(dof_map, format)

    # Generate code for tabulate_facet_dofs
    code["tabulate_facet_dofs"] = __generate_tabulate_facet_dofs(dof_map, format)

    # Generate code for tabulate_coordinates
    code["tabulate_coordinates"] = __generate_tabulate_coordinates(dof_map, format)

    # Generate code for num_sub_dof_maps
    code["num_sub_dof_maps"] = "%d" % dof_map.num_sub_dof_maps()

    return code

def __generate_needs_mesh_entities(dof_map, format):
    "Generate code for needs_mesh_entities"

    # Get total number of dofs per dimension
    num_dofs_per_dim = dof_map.num_dofs_per_dim()

    # Entities needed if at least one dof is associated
    code = [format["bool"](num_dofs_per_dim[dim] > 0) for dim in range(len(num_dofs_per_dim))]

    return code

def __generate_global_dimension(dof_map, format):
    "Generate code for global dimension"

    # Get total number of dofs per dimension
    num_dofs_per_dim = dof_map.num_dofs_per_dim()
    
    # Sum the number of dofs for each dimension
    terms = []
    for dim in range(len(num_dofs_per_dim)):
        n = num_dofs_per_dim[dim]
        if n == 1:
            terms += [format["num entities"](dim)]
        elif n > 1:
            terms += [format["multiply"]([str(n), format["num entities"](dim)])]

    # Special case, no terms
    if len(terms) == 0:
        code = "0"
    else:
        code = format["add"](terms)

    return code

def __generate_tabulate_dofs(dof_map, format, skip=[]):
    "Generate code for tabulate_dofs"

    # Generate code as a list of declarations
    code = []

    # Iterate over sub dofs
    offset_declared = False
    offset_code = []
    local_offset = 0
    for sub_dof_map in range(len(dof_map.entity_dofs())):

        # Get entity dofs for sub dof map
        sub_entity_dofs = dof_map.entity_dofs()[sub_dof_map]

        # Get the number of dofs per dimension for sub dof map
        num_dofs_per_dim = dof_map.num_dofs_per_dim(sub_dof_map)

        # Iterate over dimensions
        num_dofs = 0
        for dim in sub_entity_dofs:

            # Skip dimension if there are no dofs
            if num_dofs_per_dim[dim] == 0:
                continue

            # Write offset code
            code += offset_code

            # Iterate over entities in dimension
            for entity in sub_entity_dofs[dim]:

                # Iterate over dofs on entity
                for pos in range(len(sub_entity_dofs[dim][entity])):

                    # Get number of current dof
                    dof = sub_entity_dofs[dim][entity][pos]

                    # Assign dof
                    name = format["dofs"](local_offset + dof)
                    if num_dofs_per_dim[dim] > 1:
                        value = format["multiply"](["%d" % num_dofs_per_dim[dim], format["entity index"](dim, entity)])
                    else:
                        value = format["entity index"](dim, entity)
                    
                    # Add position on entity if any
                    if pos > 0:
                        value = format["add"]([value, "%d" % pos])

                    # Add offset if any
                    if offset_declared:
                        value = format["add"]([format["offset access"], value])

                    # Add declaration
                    if (dim, entity) not in skip:
                        code += [(name, value)]

                    # Count the number of dofs for sub dof map
                    num_dofs += 1

            # Update offset
            if num_dofs_per_dim[dim] > 0:

                # Compute additional offset
                if num_dofs_per_dim[dim] > 1:
                    value = format["multiply"](["%d" % num_dofs_per_dim[dim], format["num entities"](dim)])
                else:
                    value = format["num entities"](dim)

                # Add to previous offset
                if not offset_declared:
                    name = format["offset declaration"]
                    offset_declared = True
                else:
                    name = format["offset access"]
                    value = format["add"]([name, value])
                
                offset_code = [(name, value)]

        # Add to local offset
        local_offset += num_dofs 

    return code

def __generate_tabulate_facet_dofs(dof_map, format):
    "Generate code for tabulate_dofs"

    # Get the number of facets
    num_facets = dof_map.element().num_facets()

    # Get incidence
    incidence = dof_map.incidence()

    # Get topological dimension
    D = max([pair[0][0] for pair in incidence])

    # Find out which entities are incident to each facet
    incident = num_facets*[[]]
    for facet in range(num_facets):
        incident[facet] = [pair[1] for pair in incidence if incidence[pair] == True and pair[0] == (D - 1, facet)]

    # Tabulate dofs for each facet
    code = []
    for facet in range(num_facets):
        case = []
        facet_dof = 0
        local_offset = 0
        for sub_entity_dofs in dof_map.entity_dofs():
            num_dofs = 0
            for dim in sub_entity_dofs:
                for entity in sub_entity_dofs[dim]:
                    for dof in sub_entity_dofs[dim][entity]:
                        if (dim, entity) in incident[facet]:
                            name = format["dofs"](facet_dof)
                            value = "%d" % (local_offset + dof)
                            case += [(name, value)]
                            facet_dof += 1
                        num_dofs += 1
            local_offset += num_dofs
        code += [case]

    return code

def __generate_tabulate_coordinates(dof_map, format):
    "Generate code to compute coordinates of the dofs"

    code = []

    # Prefetch formats to speed up code generation
    format_coordinates          = format["argument coordinates"]
    format_element_coordinates  = format["element coordinates"]
    format_matrix_access        = format["matrix access"]

    # Get coordinates of the dofs (on FFC reference element)
    points = dof_map.dof_coordinates()

    # Check if we get some points from fem.dofmap.py
    if not None in points:
        #code += [format["comment"]("This function is implemented assuming affine mapping!!")]
        #code += [format["comment"]("Get cell vertices")]
        code += [format["get cell vertices"]]

        # Get the cell shape
        cell_shape = dof_map.element().cell_shape()

        # Create linear Lagrange element for the transformation
        element = FiniteElement("Lagrange", shape_to_string[cell_shape], 1)

        # Transform coordinates to FIAT element
        coordinates = [tuple([2*x - 1.0 for x in point]) for point in points]

        # Tabulate values of basisfunctions (on FIAT element)
        table = element.tabulate(0, coordinates)

        # Get matrix of values of basisfunctions at points (dof, values at dofs on linear element)
        transformed_values = numpy.transpose(table[0][(0,)*cell_shape])

        # Get shape of matrix
        shape_val = numpy.shape(transformed_values)

        # Loop dofs
        for i in range(shape_val[0]):
            for j in range(cell_shape):

                name = format_coordinates + format_matrix_access(i,j)

                values = [transformed_values[i][k] for k in range(shape_val[1])]
                symbols = [format_element_coordinates(k,j) for k in range(shape_val[1])]

                # Let inner_product handle the format
                value = inner_product(values, symbols, format)

                code += [(name, value)]

    else:
        code += [format["exception"]("tabulate_coordinates not implemented for this type of element")]

    return code
