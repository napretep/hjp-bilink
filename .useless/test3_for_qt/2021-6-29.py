import re


def bookmark_to_tag(bookmark: "list[list[int,str,int]]"):
    tag_dict = {}
    level, content, pagenum = bookmark[0][0], bookmark[0][1], bookmark[0][2]
    tag_dict[pagenum] = re.sub(r"\s", "_", content)
    level_stack = []
    level_stack.append([level, content, pagenum])
    for item in bookmark[1:]:
        level, content, pagenum = item[0], re.sub(r"\s", "_", item[1]), item[2]
        if level == 1:
            tag_dict[pagenum] = content
        else:
            while len(level_stack) != 0 and level_stack[-1][0] >= level:
                level_stack.pop()
            content = f"{level_stack[-1][1]}::{content}"
            tag_dict[pagenum] = content
        level_stack.append([level, content, pagenum])
    return tag_dict


test2 = [
    [1, '0387699031', 1],
    [2, 'Graduate Texts in Mathematics 241', 2],
    [3, 'The Arithmetic of\rDynamical Systems', 4],
    [1, 'Preface', 6],
    [2, 'Introduction', 11],
    [3, 'Exercises', 17],
    [1, '1 An Introduction to Classical Dynamics\r', 19],
    [2, '1.1 Rational Maps and the Projective Line', 19],
    [2, '1.2 Critical Points and the Riemann-HurwitzFormula', 22],
    [2, '1.3 Periodic Points and Multipliers', 28],
    [2, '1.4 The Julia Set and the Fatou Set', 32],
    [2, '1.5 Properties ofPeriodic Points', 37],
    [2, '1.6 Dynamical Systems Associated toEndomorphisms of Algebraic Groups', 38],
    [2, 'Exercises', 45],
    [1, '2 Dynamics over Local Fields: Good Reduction', 52],
    [2, '2.1 The Nonarchimedean Chordal Metric', 52],
    [2, '2.2 Periodic Points and Their Properties', 56],
    [2, '2.3 Reduction of Points and Maps Modulo p', 57], [2, '2.4 The Resultant of a Rational Map', 62],
    [2, '2.5 Rational Maps with Good Reduction', 67], [2, '2.6 Periodic Points and Good Reduction', 71],
    [2, '2.7 Periodic Points and Dynamical Units', 78],
    [2, 'Exercises', 83],
    [1, '3 Dynamics over Global Fields', 89],
    [2, '3.1 Height Functions', 89], [2, '3.2 Height Functions and Geometry', 97],
    [2, '3.3 The Uniform Boundedness Conjecture', 103],
    [2, '3.4 Canonical Heights and Dynamical Systems', 105],
    [2, '3.5 Local Canonical Heights', 110],
    [2, '3.6 Diophantine Approximation', 112], [2, '3.7 Integral Points in Orbits', 116],
    [2, '3.8 Integrality Estimates for Points in Orbits', 120],
    [2, '3.9 Periodic Points and Galois Groups', 130],
    [2, '3.10 Equidistribution and Preperiodic Points', 134],
    [2, '3.11 Ramification and Units in Dynatomic Fields', 137], [2, 'Exercises', 143],
    [1, '4 Families of Dynamical Systems', 155],
    [2, '4.1 Dynatomic Polynomials', 156],
    [2, '4.2 Quadratic Polynomials and Dynatomic Modular Curves', 163]]
if __name__ == "__main__":
    import json

    d = bookmark_to_tag(test2)
    print(json.dumps(d))
