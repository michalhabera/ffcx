// This code conforms with the UFC specification version 2018.2.0.dev0
// and was automatically generated by FFC version 2019.2.0.dev0.
//
// This code was generated with the following parameters:
//
//  {'epsilon': 1e-14,
//   'external_include_dirs': '',
//   'external_includes': '',
//   'precision': None,
//   'quadrature_degree': None,
//   'quadrature_rule': None,
//   'representation': 'uflacs',
//   'scalar_type': 'double',
//   'timeout': 10}


#pragma once

typedef double fenics_scalar_t;
#include <fenics_interface.h>

#ifdef __cplusplus
extern "C" {
#endif

fenics_finite_element* create_ffc_element_4bd6effd756a2edc2c1d9e95612f8965cc104ed8_finite_element_main(void);

fenics_finite_element* create_ffc_element_6b9c5e3e6135b592c63466d109b51cc863995cd5_finite_element_main(void);

fenics_finite_element* create_ffc_element_38cd9d5548552c34e918b04d2a94b518b9dea298_finite_element_main(void);

fenics_dofmap* create_ffc_element_4bd6effd756a2edc2c1d9e95612f8965cc104ed8_dofmap_main(void);

fenics_dofmap* create_ffc_element_6b9c5e3e6135b592c63466d109b51cc863995cd5_dofmap_main(void);

fenics_dofmap* create_ffc_element_38cd9d5548552c34e918b04d2a94b518b9dea298_dofmap_main(void);

fenics_coordinate_mapping* create_ffc_coordinate_mapping_9f20a16c62fae16e1a6c0cfb318f35fd244041c3_coordinate_mapping_main(void);

fenics_integral* create_conditional_cell_integral_e8ff290d5bcd248cdffa15cd790026dc21ea8312_otherwise(void);

fenics_form* create_conditional_form_e8ff290d5bcd248cdffa15cd790026dc21ea8312(void);


// Typedefs for convenience pointers to functions (factories)
typedef fenics_function_space* (*fenics_function_space_factory_ptr)(void);
typedef fenics_form* (*fenics_form_factory_ptr)(void);

// Coefficient spaces helpers (number: 0)

// Form function spaces helpers (form 'L')
fenics_function_space* Conditional_form_L_functionspace_0_create(void);

/* Coefficient function space typedefs for form "form_L" */
/*   - No form coefficients */
/*    Form helper */
static const fenics_form_factory_ptr Conditional_form_L_create = create_conditional_form_e8ff290d5bcd248cdffa15cd790026dc21ea8312;

/*    Typedefs (function spaces for form_L) */
static const fenics_function_space_factory_ptr Conditional_form_L_testspace_create = Conditional_form_L_functionspace_0_create;


 /* End coefficient typedefs */

/* Start high-level typedefs */
static const fenics_form_factory_ptr Conditional_linearform_create = Conditional_form_L_create;

static const fenics_function_space_factory_ptr Conditional_functionspace_create = Conditional_form_L_functionspace_0_create;
/* End high-level typedefs */


#ifdef __cplusplus
}
#endif