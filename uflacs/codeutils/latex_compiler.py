
from ufl.classes import Terminal, Indexed, SpatialDerivative
from ufl.algorithms import Graph, expand_indices, strip_variables
from uflacs.codeutils.format_code import format_code, Indented
from uflacs.codeutils.code_formatter import CodeFormatter
from uflacs.codeutils.latex_format import LatexFormatterRules

def format_integral(integral, integrandcode):
    m = integral.measure()
    dt = m.domain_type()
    if dt == 'cell':
        domain = r"\Omega_{%d}" % m.domain_id()
        dx = m._domain_types[dt]
    elif dt == 'exterior_facet':
        domain = r"\partial\Omega_{%d}" % m.domain_id()
        dx = m._domain_types[dt]
    elif dt == 'interior_facet':
        domain = r"\Gamma_{%d}" % m.domain_id()
        dx = m._domain_types[dt]
    return r"\int_{%s} %s %s" % (domain, integrandcode, dx)

def compile_form(form):

    # In this dictionary we will place ufl expression to LaTeX
    # variable name mappings while building the program
    variables = {}

    # This formatter is a multifunction with single operator
    # formatting rules for generic C++ formatting
    latex_formatter = LatexFormatterRules()

    # This final formatter implements a generic framework handling indices etc etc.
    code_formatter = CodeFormatter(latex_formatter, variables)

    # First we preprocess the form in standard UFL fashion
    fd = form.compute_form_data()

    # We'll place all code in a list while building the program
    code = []

    # Then we iterate over the integrals
    for data in fd.integral_data:
        domain_type, domain_id, integrals, metadata = data
        form_integrals = []
        for itg in integrals:
            # Fetch the expression
            integrand = itg.integrand()

            # Then we apply the additional expand_indices preprocessing that form preprocessing does not
            expr = expand_indices(integrand)
            expr = strip_variables(expr)

            # And build the computational graph of the expression
            G = Graph(expr)
            V, E = G

            integral_code = []

            def accept(v):
                if isinstance(v, (Terminal, Indexed, SpatialDerivative)):
                    return False
                if v in variables:
                    return False
                return v.shape() == ()

            nv = len(V)
            vnum = 0
            for i, v in enumerate(V):
                # Check if we should make a variable here
                if accept(v):
                    vname = 't_{%d}' % vnum
                    lastvname = vname
                    vnum += 1
                else:
                    vname = None

                # If so, generate code for it
                if vname is not None:
                    vcode = code_formatter.visit(v)
                    integral_code.append("%s = %s \\\\" % (vname, vcode))
                    code_formatter.variables[v] = vname

            # Join expressions to overall code
            code.append(integral_code)
            # Render integral and remember it for joining after the loop
            itgcode = format_integral(itg, lastvname)
            form_integrals.append(itgcode)

        # Render form by joining integrals
        formname = 'a' # FIXME
        formexprcode = '\\\\\n    &+'.join(form_integrals)
        code.append((formname, ' = ', formexprcode))

    return format_code(code)
