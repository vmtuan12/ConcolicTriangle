def triangleCheck(a, b, c):
    if (a <= 0 or b <= 0 or c <= 0):
        print("Invalid")
    elif (a + b <= c or a + c <= b or b + c <= a):
        print("Valid but not a triangle")
    else:
        if a == b and b == c:
            print("equilateral")
        elif ((a == b) or (a == c) or (b == c)):
            print("isosceles")
        elif ((a*a + b*b == c*c) or (a*a + c*c == b*b) or (b*b + c*c == a*a)):
            print('right-angled')
        else:
            print("scalene")