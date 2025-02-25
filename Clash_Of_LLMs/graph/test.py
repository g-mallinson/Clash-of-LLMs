def switch(A):
        if A == 'Blue':
            return 'Red'
        return 'Blue'    

def influence(A1, A2, U1, U2):
        print(f"BEFORE: SUP NODE A = {A1} U = {U1} influences INF NODE A = {A2} U = {U2}")
        if (A1 == A2):
            if (U2 >= 0):
                if (U1 >= 0):
                    U2 = U2 - (U2 - U1)/5     # Change of unceratinty is 20% of the difference in uncertainty
                elif (U1 > -0.5):
                    U2 = U2 - (U2 - U1)/4     # Change of unceratinty is 25% of the difference in uncertainty
                else:
                    U2 = U2 - (U2 - U1)/3     # Change of unceratinty is 33.33% of the difference in uncertainty
            elif (U2 > -0.5):
                if (U1 > -0.5):
                    U2 = U2 - (U2 - U1)/10    # Change of unceratinty is 10% of the difference in uncertainty
                else:
                    U2 = U2 - (U2 - U1)/5     # Change of unceratinty is 20% of the difference in uncertainty
            else:
                U2 = U2 - (U2 - U1)/10        # Change of unceratinty is 10% of the difference in uncertainty
        elif A2 == 'Neutral':
            U2 = 0
            A2 = A1
        else:
            if (U2 >= 0):
                if (U1 >= 0):
                    if (U2 + (U2 - U1)/5 > 1):
                        A2 = switch(A2)
                        U2 = 2 - (U2 + (U2 - U1)/5)
                    else:
                        U2 = U2 + (U2 - U1)/5     # Change of unceratinty is 20% of the difference in uncertainty
                elif (U1 > -0.5):
                    if (U2 + (U2 - U1)/4 > 1):
                        A2 = switch(A2)
                        U2 = 2 - (U2 + (U2 - U1)/4)
                    else:
                        U2 = U2 + (U2 - U1)/4     # Change of unceratinty is 25% of the difference in uncertainty
                else:
                    if (U2 + (U2 - U1)/3 > 1):
                        A2 = switch(A2)
                        U2 = 2 - (U2 + (U2 - U1)/3)
                    else:
                        U2 = U2 + (U2 - U1)/3     # Change of unceratinty is 33.33% of the difference in uncertainty
            elif (U2 > -0.5):
                if (U1 > -0.5):
                    U2 = U2 + (U2 - U1)/10    # Change of unceratinty is 10% of the difference in uncertainty
                else:
                    U2 = U2 + (U2 - U1)/5     # Change of unceratinty is 20% of the difference in uncertainty
            else:
                U2 = U2 + (U2 - U1)/10        # Change of unceratinty is 10% of the difference in uncertainty
        print(f"AFTER: SUP NODE A = {A1} U = {U1} influences INF NODE A = {A2} U = {U2}")

test_arr = [['Red', -0.8], ['Red', -0.011277994], ['Red', 0], ['Red', 0.4], ['Red', 0.9], ['Blue', -0.9], ['Blue', -0.2], ['Blue', 0], ['Blue', 0.5], ['Blue', 1.0], ['Neutral', 2.0], ['Neutral', 2.0]]
for i in range(len(test_arr)):
    for j in range(len(test_arr)):
        if i == j:
            continue
        if test_arr[i][1] < test_arr[j][1]:
            influence(test_arr[i][0], test_arr[j][0], test_arr[i][1], test_arr[j][1])
