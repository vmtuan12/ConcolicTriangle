def get_average(arr, n):
    avg = 0
    temp = 0
    if (n > 0):
        for i in range(n):
            temp += arr[i]
        avg = temp/n
    return avg